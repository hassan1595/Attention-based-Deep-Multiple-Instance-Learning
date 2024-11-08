import argparse
import numpy as np
import os


def main():
    args = get_args()
    create_mnist(**args)

def create_mnist(target_number, mean_bag_length = 10, var_bag_length= 2
    , seed = 42, num_bag_train = 2000, num_bag_test= 200):
    
    r = np.random.RandomState(seed)

    mnist_labels = np.load(os.path.join(os.getcwd(), "data", "datasets", "MNIST", "MNIST_labels.npy"))

    #ranges from where to pick the training/test samples
    range_data_train= (0, 60000)
    range_data_test= (60000, 70000)




    label_of_last_bag = 0

    # create and store training bags
    bags_created = 0
    bag_ids_train = []
    while bags_created < num_bag_train:
        bag_length = int(r.normal(mean_bag_length, var_bag_length, 1))
        if bag_length < 1:
            bag_length = 1
        
        indices = r.randint(range_data_train[0], range_data_train[1], bag_length)
        labels_in_bag = mnist_labels[indices]

        if (target_number in labels_in_bag) and (label_of_last_bag == 0):
            # only create a positive bag if the previous one has been negative
            bag_ids_train.append(indices)
            label_of_last_bag = 1
            bags_created += 1
        elif label_of_last_bag == 1:
            # force the creation of a negative bag, if the last one has been positive
            index_list = []
            bag_length_counter = 0
            while bag_length_counter < bag_length:
                index = r.randint(range_data_train[0], range_data_train[1], 1)[0]
                label_temp = mnist_labels[index]
                if label_temp != target_number:
                    index_list.append(index)
                    bag_length_counter += 1

            bag_ids_train.append(index_list)
            label_of_last_bag = 0
            bags_created += 1
        else:
            pass
    
    np.savez(os.path.join(os.getcwd(), "data", "datasets", "MNIST", "MNIST_bag_ids_train.npz"), **{f"{i}":l for (i,l) in enumerate(bag_ids_train)})

  



    label_of_last_bag = 0

    # create and store testing bags
    bags_created = 0
    bag_ids_test = []
    while bags_created < num_bag_test:
        bag_length = int(r.normal(mean_bag_length, var_bag_length, 1))
        if bag_length < 1:
            bag_length = 1
        
        indices = r.randint(range_data_test[0], range_data_test[1], bag_length)
        labels_in_bag = mnist_labels[indices]

        if (target_number in labels_in_bag) and (label_of_last_bag == 0):
            # only create a positive bag if the previous one has been negative
            bag_ids_test.append(indices)
            label_of_last_bag = 1
            bags_created += 1
        elif label_of_last_bag == 1:
            # force the creation of a negative bag, if the last one has been positive
            index_list = []
            bag_length_counter = 0
            while bag_length_counter < bag_length:
                index = r.randint(range_data_test[0], range_data_test[1], 1)[0]
                label_temp = mnist_labels[index]
                if label_temp != target_number:
                    index_list.append(index)
                    bag_length_counter += 1

            bag_ids_test.append(index_list)
            label_of_last_bag = 0
            bags_created += 1
        else:
            pass
    
    np.savez(os.path.join(os.getcwd(), "data", "datasets", "MNIST", "MNIST_bag_ids_test.npz"), **{f"{i}":l for (i,l) in enumerate(bag_ids_test)})

    

def get_args() -> argparse.Namespace:
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--target-number', default=9, type=int)
    parser.add_argument('--mean-bag-length', default=10, type=int)
    parser.add_argument('--var-bag-length', default=2, type=int)
    parser.add_argument('--seed', default=42, type=int)
    parser.add_argument('--num-bag', default=2000, type=int)
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    main()