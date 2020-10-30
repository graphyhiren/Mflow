#
# Trains an MNIST digit recognizer using PyTorch Lightning,
# and uses Mlflow to log metrics, params and artifacts
# NOTE: This example requires you to first install
# pytorch-lightning (using pip install pytorch-lightning)
#       and mlflow (using pip install mlflow).
#
# pylint: disable=arguments-differ
# pylint: disable=unused-argument
# pylint: disable=abstract-method
import pytorch_lightning as pl
import torch
import mlflow.pytorch
from argparse import ArgumentParser
from pytorch_lightning.metrics.functional import accuracy
from torch.nn import functional as F
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms


class MNISTDataModule(pl.LightningDataModule):
    def __init__(self, **kwargs):
        """
        Initialization of inherited lightning data module
        """
        super(MNISTDataModule, self).__init__()
        self.df_train = None
        self.df_val = None
        self.df_test = None
        self.train_data_loader = None
        self.val_data_loader = None
        self.test_data_loader = None
        self.args = kwargs

        # transforms for images
        self.transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
        )

    def prepare_data(self):
        """
        Implementation of abstract class
        """
        pass

    def setup(self, stage=None):
        """
        Downloads the data, parse it and split the data into train, test, validation data

        :param stage: Stage - training or testing
        """

        self.df_train = datasets.MNIST(
            "dataset", download=True, train=True, transform=self.transform
        )
        self.df_train, self.df_val = random_split(self.df_train, [55000, 5000])
        self.df_test = datasets.MNIST(
            "dataset", download=True, train=False, transform=self.transform
        )

    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Returns the review text and the targets of the specified item

        :param parent_parser: Application specific parser

        :return: Returns the augmented arugument parser
        """
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument(
            "--batch-size",
            type=int,
            default=16,
            metavar="N",
            help="input batch size for training (default: 16)",
        )
        parser.add_argument(
            "--num-workers",
            type=int,
            default=3,
            metavar="N",
            help="number of workers (default: 0)",
        )
        return parser

    def create_data_loader(self, df):
        """
        Generic data loader function

        :param df: Input tensor

        :return: Returns the constructed dataloader
        """
        return DataLoader(
            df, batch_size=self.args["batch_size"], num_workers=self.args["num_workers"],
        )

    def train_dataloader(self):
        """
        :return: output - Train data loader for the given input
        """
        return self.create_data_loader(self.df_train)

    def val_dataloader(self):
        """
        :return: output - Validation data loader for the given input
        """
        return self.create_data_loader(self.df_val)

    def test_dataloader(self):
        """
        :return: output - Test data loader for the given input
        """
        return self.create_data_loader(self.df_test)


class LightningMNISTClassifier(pl.LightningModule):
    def __init__(self, **kwargs):
        """
        Initializes the network
        """
        super(LightningMNISTClassifier, self).__init__()

        # mnist images are (1, 28, 28) (channels, width, height)
        self.optimizer = None
        self.scheduler = None
        self.layer_1 = torch.nn.Linear(28 * 28, 128)
        self.layer_2 = torch.nn.Linear(128, 256)
        self.layer_3 = torch.nn.Linear(256, 10)
        self.args = kwargs

    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument(
            "--batch-size",
            type=int,
            default=64,
            metavar="N",
            help="input batch size for training (default: 64)",
        )
        parser.add_argument(
            "--num-workers",
            type=int,
            default=3,
            metavar="N",
            help="number of workers (default: 3)",
        )
        parser.add_argument(
            "--lr", type=float, default=1e-3, metavar="LR", help="learning rate (default: 1e-3)",
        )
        return parser

    def forward(self, x):
        """
        :param x: Input data

        :return: output - mnist digit label for the input image
        """
        batch_size = x.size()[0]

        # (b, 1, 28, 28) -> (b, 1*28*28)
        x = x.view(batch_size, -1)

        # layer 1 (b, 1*28*28) -> (b, 128)
        x = self.layer_1(x)
        x = torch.relu(x)

        # layer 2 (b, 128) -> (b, 256)
        x = self.layer_2(x)
        x = torch.relu(x)

        # layer 3 (b, 256) -> (b, 10)
        x = self.layer_3(x)

        # probability distribution over labels
        x = torch.log_softmax(x, dim=1)

        return x

    def cross_entropy_loss(self, logits, labels):
        """
        Initializes the loss function

        :return: output - Initialized cross entropy loss function
        """
        return F.nll_loss(logits, labels)

    def training_step(self, train_batch, batch_idx):
        """
        Training the data as batches and returns training loss on each batch

        :param train_batch: Batch data
        :param batch_idx: Batch indices

        :return: output - Training loss
        """
        x, y = train_batch
        logits = self.forward(x)
        loss = self.cross_entropy_loss(logits, y)
        return {"loss": loss}

    def validation_step(self, val_batch, batch_idx):
        """
        Performs validation of data in batches

        :param val_batch: Batch data
        :param batch_idx: Batch indices

        :return: output - valid step loss
        """
        x, y = val_batch
        logits = self.forward(x)
        loss = self.cross_entropy_loss(logits, y)
        return {"val_loss": loss}

    def validation_epoch_end(self, outputs):
        """
        Computes average validation accuracy

        :param outputs: outputs after every epoch end

        :return: output - average valid loss
        """
        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()
        self.log("val_loss", avg_loss)

    def test_step(self, test_batch, batch_idx):
        """
        Performs test and computes the accuracy of the model

        :param test_batch: Batch data
        :param batch_idx: Batch indices

        :return: output - Testing accuracy
        """
        x, y = test_batch
        output = self.forward(x)
        _, y_hat = torch.max(output, dim=1)
        test_acc = accuracy(y_hat.cpu(), y.cpu())
        return {"test_acc": test_acc}

    def test_epoch_end(self, outputs):
        """
        Computes average test accuracy score

        :param outputs: outputs after every epoch end

        :return: output - average test loss
        """
        avg_test_acc = torch.stack([x["test_acc"] for x in outputs]).mean()
        self.log("avg_test_acc", avg_test_acc)

    def prepare_data(self):
        """
        Prepares the data for training and prediction
        """
        return {}

    def configure_optimizers(self):
        """
        Initializes the optimizer and learning rate scheduler

        :return: output - Initialized optimizer and scheduler
        """
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.args["lr"])
        self.scheduler = {
            "scheduler": torch.optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer, mode="min", factor=0.2, patience=2, min_lr=1e-6, verbose=True,
            ),
            "monitor": "val_loss",
        }
        return [self.optimizer], [self.scheduler]

    def optimizer_step(
        self,
        epoch,
        batch_idx,
        optimizer,
        optimizer_idx,
        second_order_closure=None,
        on_tpu=False,
        using_lbfgs=False,
        using_native_amp=False,
    ):
        """
        Training step function which runs for the given number of epochs

        :param epoch: Number of epochs to train
        :param batch_idx: batch indices
        :param optimizer: Optimizer to be used in training step
        """
        self.optimizer.step()
        self.optimizer.zero_grad()


if __name__ == "__main__":
    parser = ArgumentParser(description="PyTorch autolog Mnist Example")

    # Add trainer specific arguments
    parser.add_argument(
        "--max-epochs", type=int, default=5, help="number of epochs to run (default: 5)"
    )
    parser.add_argument(
        "--gpus", type=int, default=0, help="Number of gpus - by default runs on CPU"
    )
    parser.add_argument(
        "--accelerator", type=str, default=None, help="Accelerator - (default: None)",
    )
    parser = LightningMNISTClassifier.add_model_specific_args(parent_parser=parser)

    mlflow.pytorch.autolog(log_every_n_iter=2)

    args = parser.parse_args()
    dict_args = vars(args)

    dm = MNISTDataModule(**dict_args)
    dm.prepare_data()
    dm.setup(stage="fit")

    model = LightningMNISTClassifier(**dict_args)
    trainer = pl.Trainer.from_argparse_args(args)
    trainer.fit(model, dm)
    trainer.test()
