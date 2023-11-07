import torch
import torch.nn as nn
from torch import optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
import torch.nn.functional as F

from torch_geometric.nn import Set2Set

from embedder import embedder
from layers import GatherModel
from utils import create_batch_mask

from torch_scatter import scatter_mean, scatter_add, scatter_std

class GIB_DS_ModelTrainer(embedder):
    def __init__(self, args, train_df, valid_df, test_df, repeat, fold):
        embedder.__init__(self, args, train_df, valid_df, test_df, repeat, fold)

        self.model = GIB_DS(device = self.device, num_step_message_passing = self.args.message_passing).to(self.device)
        self.optimizer = optim.Adam(params = self.model.parameters(), lr = self.args.lr, weight_decay = self.args.weight_decay)
        self.scheduler = ReduceLROnPlateau(self.optimizer, patience=self.args.patience, mode='min', verbose=True)
          
    def train(self):        
        
        loss_fn = torch.nn.MSELoss()
        
        for epoch in range(1, self.args.epochs + 1):
            self.model.train()
            self.train_loss = 0
            solute_preserve = 0
            solvent_preserve = 0
            for bc, samples in enumerate(self.train_loader):
                self.optimizer.zero_grad()
                masks = create_batch_mask(samples)
                
                outputs, _ = self.model([samples[0].to(self.device), samples[1].to(self.device), masks[0].to(self.device), masks[1].to(self.device)])
                loss = loss_fn(outputs, samples[2].reshape(-1, 1).to(self.device).float())

                # Information Bottleneck

                outputs, solute_KL_Loss, solvent_KL_Loss, solute_preserve_rate, solvent_preserve_rate = self.model([samples[0].to(self.device), samples[1].to(self.device), masks[0].to(self.device), masks[1].to(self.device)], bottleneck = True)
                loss += loss_fn(outputs, samples[2].reshape(-1, 1).to(self.device).float())
                loss += self.args.beta * solute_KL_Loss
                loss += self.args.beta * solvent_KL_Loss
                #loss += self.args.beta * solvent_pred_loss

                loss.backward()
                self.optimizer.step()
                self.train_loss += loss
                solute_preserve += solute_preserve_rate
                solvent_preserve += solvent_preserve_rate

            self.model.eval()
            self.evaluate(epoch)

            self.scheduler.step(self.val_loss)

            # Write Statistics
            self.writer.add_scalar("stats/solute_preservation", solute_preserve/bc, epoch)
            self.writer.add_scalar("stats/solvent_preservation", solvent_preserve/bc, epoch)

            # Early stopping
            if len(self.best_val_losses) > int(self.args.es / self.args.eval_freq):
                if self.best_val_losses[-1] == self.best_val_losses[-int(self.args.es / self.args.eval_freq)]:
                    self.is_early_stop = True
                    break

        self.evaluate(epoch, final = True)
        self.writer.close()
        
        return self.best_test_loss, self.best_test_mae_loss


class GIB_DS(nn.Module):
    """
    This the main class for CIGIN model
    """

    def __init__(self,
                device,
                node_input_dim=52,
                edge_input_dim=10,
                node_hidden_dim=52,
                edge_hidden_dim=52,
                num_step_message_passing=3,
                interaction='dot',
                num_step_set2_set=2,
                num_layer_set2set=1,
                ):
        super(GIB_DS, self).__init__()

        self.device = device

        self.node_input_dim = node_input_dim
        self.node_hidden_dim = node_hidden_dim
        self.edge_input_dim = edge_input_dim
        self.edge_hidden_dim = edge_hidden_dim
        self.num_step_message_passing = num_step_message_passing
        self.interaction = interaction

        self.solute_gather = GatherModel(self.node_input_dim, self.edge_input_dim,
                                         self.node_hidden_dim, self.edge_input_dim,
                                         self.num_step_message_passing,
                                         )
        self.solvent_gather = GatherModel(self.node_input_dim, self.edge_input_dim,
                                          self.node_hidden_dim, self.edge_input_dim,
                                          self.num_step_message_passing,
                                          )

        self.predictor = nn.Sequential(
            nn.Linear(8 * self.node_hidden_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

        self.solute_compressor = nn.Sequential(
            nn.Linear(2 * self.node_hidden_dim, self.node_hidden_dim),
            nn.BatchNorm1d(self.node_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.node_hidden_dim, 1)
            )

        self.solvent_compressor = nn.Sequential(
            nn.Linear(2 * self.node_hidden_dim, self.node_hidden_dim),
            nn.BatchNorm1d(self.node_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.node_hidden_dim, 1)
            )    
        
        self.solvent_predictor = nn.Linear(4 * self.node_hidden_dim, 4 * self.node_hidden_dim)
        
        self.mse_loss = torch.nn.MSELoss()

        self.num_step_set2set = num_step_set2_set
        self.num_layer_set2set = num_layer_set2set
        self.set2set_solute = Set2Set(2 * node_hidden_dim, self.num_step_set2set)
        self.set2set_solvent = Set2Set(2 * node_hidden_dim, self.num_step_set2set)

        self.init_model()
    
    def init_model(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                torch.nn.init.xavier_uniform_(m.weight.data)
                if m.bias is not None:
                    m.bias.data.fill_(0.0)
    
    def solute_compress(self, solute_features):
        
        p = self.solute_compressor(solute_features)
        temperature = 1.0
        bias = 0.0 + 0.0001  # If bias is 0, we run into problems
        eps = (bias - (1 - bias)) * torch.rand(p.size()) + (1 - bias)
        gate_inputs = torch.log(eps) - torch.log(1 - eps)
        gate_inputs = gate_inputs.to(self.device)
        gate_inputs = (gate_inputs + p) / temperature
        gate_inputs = torch.sigmoid(gate_inputs).squeeze()

        return gate_inputs, p

    def solvent_compress(self, solvent_features):
        
        p = self.solvent_compressor(solvent_features)
        temperature = 1.0
        bias = 0.0 + 0.0001  # If bias is 0, we run into problems
        eps = (bias - (1 - bias)) * torch.rand(p.size()) + (1 - bias)
        gate_inputs = torch.log(eps) - torch.log(1 - eps)
        gate_inputs = gate_inputs.to(self.device)
        gate_inputs = (gate_inputs + p) / temperature
        gate_inputs = torch.sigmoid(gate_inputs).squeeze()

        return gate_inputs, p
    
    
    def forward(self, data, bottleneck = False, test = False):
        solute = data[0]
        solvent = data[1]
        solute_len = data[2]
        solvent_len = data[3]
 
 
        # node embeddings after interaction phase
        solute_features = self.solute_gather(solute)
        solvent_features = self.solvent_gather(solvent)

        # Add normalization
        self.solute_features = F.normalize(solute_features, dim = 1)
        self.solvent_features = F.normalize(solvent_features, dim = 1)

        # Interaction phase
        len_map = torch.sparse.mm(solute_len.t(), solvent_len)

        interaction_map = torch.mm(self.solute_features, self.solvent_features.t())
        ret_interaction_map = torch.clone(interaction_map)
        ret_interaction_map = interaction_map * len_map.to_dense()
        interaction_map = interaction_map * len_map.to_dense()

        self.solvent_prime = torch.mm(interaction_map.t(), self.solute_features)
        self.solute_prime = torch.mm(interaction_map, self.solvent_features)

        # Prediction phase
        self.solute_features = torch.cat((self.solute_features, self.solute_prime), dim=1)
        self.solvent_features = torch.cat((self.solvent_features, self.solvent_prime), dim=1)

        if test:

            _, self.solute_importance = self.solute_compress(self.solute_features)
            _, self.solvent_importance = self.solvent_compress(self.solute_features)

        if bottleneck:
            
            lambda_pos, p = self.solute_compress(self.solute_features)
            lambda_pos = lambda_pos.reshape(-1, 1)
            lambda_neg = 1 - lambda_pos

            # Get Stats (solute)
            solute_preserve_rate = (torch.sigmoid(p) > 0.5).float().mean()

            static_solute_feature = self.solute_features.clone().detach()
            node_feature_mean = scatter_mean(static_solute_feature, solute.batch, dim = 0)[solute.batch]
            node_feature_std = scatter_std(static_solute_feature, solute.batch, dim = 0)[solute.batch]
            
            noisy_node_feature_mean = lambda_pos * self.solute_features + lambda_neg * node_feature_mean
            noisy_node_feature_std = lambda_neg * node_feature_std

            noisy_node_feature = noisy_node_feature_mean + torch.rand_like(noisy_node_feature_mean) * noisy_node_feature_std
            noisy_solute_subgraphs = self.set2set_solute(noisy_node_feature, solute.batch)

            epsilon = 1e-7

            KL_tensor = 0.5 * scatter_add(((noisy_node_feature_std ** 2) / (node_feature_std + epsilon) ** 2).mean(dim = 1), solute.batch).reshape(-1, 1) + \
                        scatter_add((((noisy_node_feature_mean - node_feature_mean)/(node_feature_std + epsilon)) ** 2), solute.batch, dim = 0)
            solute_KL_Loss = torch.mean(KL_tensor)

            # Get Stats (solvent)
            lambda_pos, p = self.solvent_compress(self.solvent_features)
            lambda_pos = lambda_pos.reshape(-1, 1)
            lambda_neg = 1 - lambda_pos

            # Get Stats (solute)
            solvent_preserve_rate = (torch.sigmoid(p) > 0.5).float().mean()

            static_solvent_feature = self.solvent_features.clone().detach()
            node_feature_mean = scatter_mean(static_solvent_feature, solvent.batch, dim = 0)[solvent.batch]
            node_feature_std = scatter_std(static_solvent_feature, solvent.batch, dim = 0)[solvent.batch]
            
            noisy_node_feature_mean = lambda_pos * self.solvent_features + lambda_neg * node_feature_mean
            noisy_node_feature_std = lambda_neg * node_feature_std

            noisy_node_feature = noisy_node_feature_mean + torch.rand_like(noisy_node_feature_mean) * noisy_node_feature_std
            noisy_solvent_subgraphs = self.set2set_solvent(noisy_node_feature, solvent.batch)

            epsilon = 1e-7

            KL_tensor = 0.5 * scatter_add(((noisy_node_feature_std ** 2) / (node_feature_std + epsilon) ** 2).mean(dim = 1), solvent.batch).reshape(-1, 1) + \
                        scatter_add((((noisy_node_feature_mean - node_feature_mean)/(node_feature_std + epsilon)) ** 2), solvent.batch, dim = 0)
            solvent_KL_Loss = torch.mean(KL_tensor)
            
            # Predict Solvent
            # self.solvent_features_s2s = self.set2set_solvent(self.solvent_features, solvent.batch)
            # solvent_pred_loss = self.mse_loss(self.solvent_features_s2s, self.solvent_predictor(noisy_solute_subgraphs))

            # Prediction Y
            final_features = torch.cat((noisy_solute_subgraphs, noisy_solvent_subgraphs), 1)
            predictions = self.predictor(final_features)

            return predictions, solute_KL_Loss, solvent_KL_Loss, solute_preserve_rate, solvent_preserve_rate
        
        else:

            self.solute_features_s2s = self.set2set_solute(self.solute_features, solute.batch)
            self.solvent_features_s2s = self.set2set_solvent(self.solvent_features, solvent.batch)

            final_features = torch.cat((self.solute_features_s2s, self.solvent_features_s2s), 1)
            predictions = self.predictor(final_features)
        
            return predictions, ret_interaction_map
    
    def get_checkpoints(self):
        
        return self.solute_features_s2s, self.solvent_features_s2s, self.solute_importance, self.solvent_importance