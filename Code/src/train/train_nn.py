## Author: Wu Bolun
## email: bowenwu@sjtu.edu.cn
## date: 2020.6.5

import copy
import time

import json
import numpy as np
import torch
import torch.nn.functional as F
from torch import nn, optim
from torch.utils import data

from dataset import MalwareDataset


class FcNet(nn.Module):
    def __init__(self, input_size, num_classes):
        super(FcNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 32)
        self.fc3 = nn.Linear(32, num_classes)
        self.softmax = nn.Softmax()
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.softmax(x)
        return x
            

def train_model(model, criterion, optimizer, schedular, num_epochs=25):
    epoch_loss_recorder = []
    epoch_acc_recorder = []

    start_time = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs-1))
        print('-' * 18)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()
            
            running_loss = 0.0
            running_corrects = 0

            for i, data in enumerate(malware_dataloader[phase]):  #TODO Dataloader
                inputs = data['vector'].to(device)
                labels = data['type'].to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs.float())
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels)
            
            if phase == 'train' and schedular:
                schedular.step()
            
            epoch_loss = running_loss / malware_datasize[phase] # TODO
            epoch_acc = running_corrects.double() / malware_datasize[phase]

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(phase, epoch_loss, epoch_acc))

            if phase == 'val':
                epoch_loss_recorder.append(epoch_loss)
                epoch_acc_recorder.append(epoch_acc.item())

            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

                tmp_save_path = 'model/nn_{}.pth'.format(epoch) # TODO
                torch.save(model.state_dict(), tmp_save_path)

        
        print()
    
    time_elapsed = time.time() - start_time
    print('Training complete in {:.0f}m {:.0f}s'.format(time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    model.load_state_dict(best_model_wts)
    return model, epoch_loss_recorder, epoch_acc_recorder


if __name__ == '__main__':
    # gpu
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # data
    malware_dataloader = {
        x: data.DataLoader(MalwareDataset(mode=x), batch_size=32, shuffle=True)
        for x in ['train', 'val']
    }
    malware_datasize = {'train': 1010, 'val': 280}

    # net
    net = FcNet(input_size=467, num_classes=2).to(device)
    model_path = 'model/best.pth'
    # net.load_state_dict(torch.load(model_path))

    # loss and optim
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-4)

    model_best, epoch_loss_recorder, epoch_acc_recorder = train_model(
        net, criterion, optimizer, schedular=None, num_epochs=60)

    # save model
    PATH = 'model/final.pth'
    torch.save(model_best.state_dict(), PATH)

    with open('loss.log', 'w') as f:
        json.dump(epoch_loss_recorder, f)
    with open('acc.log', 'w') as f:
        json.dump(epoch_acc_recorder, f)



