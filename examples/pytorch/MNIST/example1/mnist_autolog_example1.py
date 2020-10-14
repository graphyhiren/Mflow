#
# Trains an MNIST digit recognizer using PyTorch Lightning,
# and uses Mlflow to log metrics, params and artifacts
# NOTE: This example requires you to first install
# pytorch-lightning (using pip install pytorch-lightning)
#       and mlflow (using pip install mlflow).
#
import pytorch_lightning as pl
import os
import mlflow
import torch
from argparse import ArgumentParser
from mlflow.pytorch.pytorch_autolog import autolog
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.callbacks import LearningRateLogger
from pytorch_lightning.metrics.functional import accuracy
from torch.nn import functional as F
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms


class LightningMNISTClassifier(pl.LightningModule):
    def __init__(self, **kwargs):
        """
        Initializes the network
        """
        super(LightningMNISTClassifier, self).__init__()

        # mnist images are (1, 28, 28) (channels, width, height)
        self.layer_1 = torch.nn.Linear(28 * 28, 128)
        self.layer_2 = torch.nn.Linear(128, 256)
        self.layer_3 = torch.nn.Linear(256, 10)
        self.args = kwargs

        # transforms for images
        self.transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
        )

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
            default=1,
            metavar="N",
            help="number of workers (default: 0)",
        )
        parser.add_argument(
            "--lr",
            type=float,
            default=1e-3,
            metavar="LR",
            help="learning rate (default: 1e-3)",
        )
        return parser

    def forward(self, x):
        """
        Forward Function
        """
        batch_size, channels, width, height = x.size()

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
        Loss Fn to compute loss
        """
        return F.nll_loss(logits, labels)

    def training_step(self, train_batch, batch_idx):
        """
        training the data as batches and returns training loss on each batch
        """
        x, y = train_batch
        logits = self.forward(x)
        loss = self.cross_entropy_loss(logits, y)
        return {"loss": loss}

    def validation_step(self, val_batch, batch_idx):
        """
        Performs validation of data in batches
        """
        x, y = val_batch
        logits = self.forward(x)
        loss = self.cross_entropy_loss(logits, y)
        return {"val_step_loss": loss}

    def validation_epoch_end(self, outputs):
        """
        Computes average validation accuracy
        """
        avg_loss = torch.stack([x["val_step_loss"] for x in outputs]).mean()
        return {"val_loss": avg_loss}

    def test_step(self, test_batch, batch_idx):
        """
        Performs test and computes test accuracy
        """
        x, y = test_batch
        output = self.forward(x)
        a, y_hat = torch.max(output, dim=1)
        test_acc = accuracy(y_hat.cpu(), y.cpu())
        return {"test_acc": torch.tensor(test_acc)}

    def test_epoch_end(self, outputs):
        """
        Computes average test accuracy score
        """
        avg_test_acc = torch.stack([x["test_acc"] for x in outputs]).mean()
        return {"avg_test_acc": avg_test_acc}

    def prepare_data(self):
        """
        Preprocess the input data.
        """
        return {}

    def train_dataloader(self):
        """
        Loading training data as batches
        """
        mnist_train = datasets.MNIST(
            "dataset", download=True, train=True, transform=self.transform
        )
        return DataLoader(
            mnist_train,
            batch_size=self.args["batch_size"],
            num_workers=self.args["num_workers"],
        )

    def val_dataloader(self):
        """
        Loading validation data as batches
        """
        mnist_train = datasets.MNIST(
            "dataset", download=True, train=True, transform=self.transform
        )
        mnist_train, mnist_val = random_split(mnist_train, [55000, 5000])

        return DataLoader(
            mnist_val,
            batch_size=self.args["batch_size"],
            num_workers=self.args["num_workers"],
        )

    def test_dataloader(self):
        """
        Loading test data as batches
        """
        mnist_test = datasets.MNIST(
            "dataset", download=True, train=False, transform=self.transform
        )
        return DataLoader(
            mnist_test,
            batch_size=self.args["batch_size"],
            num_workers=self.args["num_workers"],
        )

    def configure_optimizers(self):
        """
        Creates and returns Optimizer
        """
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.args["lr"])
        self.scheduler = {
            "scheduler": torch.optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode="min",
                factor=0.2,
                patience=2,
                min_lr=1e-6,
                verbose=True,
            )
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
        self.optimizer.step()
        self.optimizer.zero_grad()


if __name__ == "__main__":
    parser = ArgumentParser(description="PyTorch Autolog Mnist Example")

    # Add trainer specific arguments

    parser.add_argument(
        "--tracking-uri", type=str, default="http://localhost:5000/", help="mlflow tracking uri"
    )
    parser.add_argument(
        "--max-epochs", type=int, default=20, help="number of epochs to run (default: 20)"
    )
    parser.add_argument(
        "--gpus", type=int, default=0, help="Number of gpus - by default runs on CPU"
    )
    parser.add_argument(
        "--distributed-backend",
        type=str,
        default=None,
        help="Distributed Backend - (default: None)",
    )
    parser = LightningMNISTClassifier.add_model_specific_args(parent_parser=parser)

    autolog()

    args = parser.parse_args()
    dict_args = vars(args)
    mlflow.set_tracking_uri(dict_args['tracking_uri'])

    model = LightningMNISTClassifier(**dict_args)
    early_stopping = EarlyStopping(monitor="val_loss", mode="min", verbose=True)

    checkpoint_callback = ModelCheckpoint(
        filepath=os.getcwd(),
        save_top_k=1,
        verbose=True,
        monitor="val_loss",
        mode="min",
        prefix="",
    )
    lr_logger = LearningRateLogger()

    trainer = pl.Trainer.from_argparse_args(
        args,
        callbacks=[lr_logger],
        early_stop_callback=early_stopping,
        checkpoint_callback=checkpoint_callback,
        train_percent_check=0.1,
    )
    trainer.fit(model)
    trainer.test()
