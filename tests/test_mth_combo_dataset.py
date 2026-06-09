import types
import unittest
from unittest import mock

from datasets import MTHCombo as mth_combo_module


class _FakeMTH1000:
    def __init__(self, mode, transform, args=None):
        self.root = args.mth1000_root
        self.samples = [
            {"id": f"{self.root}-0", "text": self.root[:1]},
            {"id": f"{self.root}-1", "text": self.root[:2]},
        ]
        self.charset = sorted(set("".join(sample["text"] for sample in self.samples)))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


class MTHComboDatasetTest(unittest.TestCase):
    def test_exposes_flattened_samples_without_changing_index_routing(self):
        args = types.SimpleNamespace(
            mth_combo_roots=["alpha", "beta"],
            mth_combo_raw_roots=["raw_alpha", "raw_beta"],
        )

        with mock.patch.object(mth_combo_module, "MTH1000", _FakeMTH1000):
            dataset = mth_combo_module.MTHCombo("train", transform=None, args=args)

        self.assertEqual(len(dataset), 4)
        self.assertEqual([sample["id"] for sample in dataset.samples], [
            "alpha-0",
            "alpha-1",
            "beta-0",
            "beta-1",
        ])
        self.assertEqual(dataset[0]["id"], "alpha-0")
        self.assertEqual(dataset[2]["id"], "beta-0")
        self.assertEqual(dataset[3]["id"], "beta-1")


if __name__ == "__main__":
    unittest.main()
