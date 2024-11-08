import argparse
import torch
import numpy as np
import os
from data.data import load_data
from data.data_utils.transformations import get_transformation
from model.model import MILModel
from model.model import MLIMNISTModel
import matplotlib.pyplot as plt
import math
from pathlib import Path
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def explain(bag, label, model, plot, dataset, pooling_type, outfolder=None, filename=None):
    bag.requires_grad_(True)

    if pooling_type == "attention" or pooling_type == "gated_attention":
        res, a = model(bag)
    else:
        res = model(bag)
    res.backward()
    sensitivty = bag.grad**2
    
    if plot:

        if dataset == "MNIST":
            num_images = bag.size()[0]
            num_columns = 5 
            num_rows = math.ceil(num_images  / num_columns)
            fig = plt.figure( figsize=(20, 2 * num_rows))
            subfigs = fig.subfigures(2, 1, wspace=0.07)

            axes_1 = subfigs[0].subplots(num_rows, num_columns)
            axes_1 = axes_1.reshape(num_rows, num_columns)
            subfigs[0].suptitle(f'Sensitivity analysis - Label: {label.item()} - Number of instances: {num_images}', fontsize = 35)


            for i, image in enumerate(sensitivty.cpu().numpy()):

                ax = axes_1[i // num_columns, i % num_columns]
                ax.imshow(image.reshape(28,28), cmap='gist_heat')
                ax.axis('off')

            for i in range(num_images, num_rows * num_columns):
                subfigs[0].delaxes(axes_1.flatten()[i])

            if pooling_type == "attention" or pooling_type == "gated_attention":
                axes_2 = subfigs[1].subplots(num_rows, num_columns)
                axes_2 = axes_2.reshape(num_rows, num_columns)
                subfigs[1].suptitle(f'Attention weights - label: {label.item()} - Number of instances: {num_images}', fontsize = 35)
                max_idx = torch.argmax(a).item()
                for i, image in enumerate(bag.cpu().detach().numpy()):

                    ax = axes_2[i // num_columns, i % num_columns]
                    ax.imshow(image.reshape(28,28), cmap='grey')
                    ax.text(0.5, -0.15, fr'$a_{i}$ = {a[i].item():.2f}', fontsize=25, ha="center", transform=ax.transAxes)
                    ax.axis('off')
                    if i == max_idx and label == 1:

                        rect = patches.Rectangle((0, 0),
                                                27, 27,
                                                linewidth=10, edgecolor='red', facecolor='none', fill=False, zorder=20)
                        ax.add_patch(rect)

                for i in range(num_images, num_rows * num_columns):
                    subfigs[1].delaxes(axes_2.flatten()[i])


        else:
            raise ValueError(f"Dataset {dataset} not supported for plotting!")

        if outfolder and filename:
            # create outfolder if not exist
            Path(outfolder).mkdir(parents=True, exist_ok=True)   
            figure = plt.gcf()  # get current figure
            figure.set_size_inches(32, 18)
            plt.savefig(os.path.join(outfolder, filename))
            plt.close()

    return sensitivty.cpu().numpy()


def main():
    args = get_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.dataset in ["MUSK1", "MUSK2", "ELEPHANT", "TIGER", "FOX"]:
        model = MILModel(args.dataset, args.mil_type, args.pooling_type, return_attentions=True)
        transformation = get_transformation(device)
    elif args.dataset == "MNIST":
        model = MLIMNISTModel(args.mil_type, args.pooling_type, return_attentions=True)
        transformation = get_transformation(device, normalization_params=255.)
    else:
        raise ValueError(f"Dataset {args.dataset} not supported!")

    model.load_state_dict(torch.load(args.model_path))
    model.to(device)

    
    _, data = load_data(args.dataset, transformation=transformation)
	
    for i in range(args.n_samples):
        bag, label = data[i]
        explain(bag, label, model, plot = True, dataset= args.dataset, outfolder=args.outfolder, filename= f'{args.dataset}_{i}_analysis_plot')
	


def get_args() -> argparse.Namespace:
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='MNIST')
    parser.add_argument('--n-samples', default= 20, type=int)
    parser.add_argument('--outfolder', default= os.path.join(os.getcwd(), "data", "plots"))
    parser.add_argument('--model-path', default=  os.path.join("model","model_parameters", "MNIST_embedding_based_attention.pt"))
    parser.add_argument('--mil-type', 
					 	default='embedding_based',
						choices=['embedding_based', 'instance_based'])
    parser.add_argument('--pooling-type', 
					 	default='attention',
						choices=['max', 'mean', 'attention', 'gated_attention'])
                        
    args = parser.parse_args()
    return args

if __name__ == '__main__':
	main()