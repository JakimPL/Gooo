import torch
import os


class LQN(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.ln1 = torch.nn.Linear(input_size, hidden_size)
        self.ln2 = torch.nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.nn.functional.relu(self.ln1(x))
        x = self.ln2(x)
        return x

    def save(self, filename='model.pth'):
        model_path = "./model"
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        filename = os.path.join(model_path, filename)
        torch.save(self.state_dict(), filename)


class QTRN:
    def __init__(self, model, learning_rate, gamma):
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
        self.loss_function = torch.nn.MSELoss()

    def train_step(self, current_state, move, reward, next_state, end):
        torch_state = torch.tensor(current_state, dtype=torch.float)
        torch_next_state = torch.tensor(next_state, dtype=torch.float)
        torch_move = torch.tensor(move, dtype=torch.long)
        torch_reward = torch.tensor(reward, dtype=torch.float)
        torch_end = end

        if len(torch_state.shape) == 1:
            torch_state = torch.unsqueeze(torch_state, 0)
            torch_next_state = torch.unsqueeze(torch_next_state, 0)
            torch_move = torch.unsqueeze(torch_move, 0)
            torch_reward = torch.unsqueeze(torch_reward, 0)
            torch_end = (end, )

        prediction = self.model(torch_state)
        clone = prediction.clone()
        for index in range(len(torch_end)):
            q = torch_reward[index]
            if not torch_end[index]:
                q = torch_reward[index] + self.gamma * torch.max(self.model(torch_next_state[index]))

            clone[index][torch.argmax(torch_move[index]).item()] = q

        self.optimizer.zero_grad()
        loss = self.loss_function(clone, prediction)
        loss.backward()

        self.optimizer.step()
