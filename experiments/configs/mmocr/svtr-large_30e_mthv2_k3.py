_base_ = ['/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_20e_st_mj.py']

load_from = None

_base_.model.encoder.update(
    dict(
        embed_dims=[192, 256, 512],
        depth=[3, 9, 9],
        num_heads=[6, 8, 16],
        mixer_types=['Local'] * 10 + ['Global'] * 11,
        out_channels=384))

_base_.model.decoder.update(dict(in_channels=384))

_base_.model.preprocessor.update(dict(output_image_size=(32, 256)))
_base_.model.encoder.update(dict(img_size=[32, 256], max_seq_len=64))

_base_.model.decoder.dictionary.update(
    dict(
        dict_file='data/mmocr_exports/mthv2/charset.txt',
        with_padding=True,
        with_unknown=False))
_base_.model.decoder.module_loss.update(
    dict(letter_case='unchanged', zero_infinity=True))

train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=30, val_interval=1)

param_scheduler = [
    dict(
        type='LinearLR',
        start_factor=0.5,
        end_factor=1.,
        end=2,
        verbose=False,
        convert_to_iter_based=True),
    dict(
        type='CosineAnnealingLR',
        T_max=29,
        begin=2,
        end=30,
        verbose=False,
        convert_to_iter_based=True),
]

train_pipeline = [
    dict(type='LoadImageFromFile', ignore_empty=True, min_size=5),
    dict(
        type='ConditionApply',
        true_transforms=[
            dict(
                type='ImgAugWrapper',
                args=[dict(cls='Rot90', k=3, keep_size=False)])
        ],
        condition="results['img_shape'][1] < results['img_shape'][0]"),
    dict(type='LoadOCRAnnotations', with_text=True),
    dict(type='Resize', scale=(256, 64)),
    dict(
        type='PackTextRecogInputs',
        meta_keys=('img_path', 'ori_shape', 'img_shape', 'valid_ratio'))
]

test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='ConditionApply',
        true_transforms=[
            dict(
                type='ImgAugWrapper',
                args=[dict(cls='Rot90', k=3, keep_size=False)])
        ],
        condition="results['img_shape'][1] < results['img_shape'][0]"),
    dict(type='Resize', scale=(256, 64)),
    dict(type='LoadOCRAnnotations', with_text=True),
    dict(
        type='PackTextRecogInputs',
        meta_keys=('img_path', 'ori_shape', 'img_shape', 'valid_ratio'))
]

train_list = [
    dict(
        type='OCRDataset',
        data_root='data',
        ann_file='mmocr_exports/mthv2/textrecog_train.json',
        pipeline=None)
]
val_list = [
    dict(
        type='OCRDataset',
        data_root='data',
        ann_file='mmocr_exports/mthv2/textrecog_val.json',
        test_mode=True,
        pipeline=None)
]
test_list = [
    dict(
        type='OCRDataset',
        data_root='data',
        ann_file='mmocr_exports/mthv2/textrecog_test.json',
        test_mode=True,
        pipeline=None)
]

train_dataloader = dict(
    batch_size=32,
    num_workers=8,
    persistent_workers=True,
    pin_memory=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        type='ConcatDataset', datasets=train_list, pipeline=train_pipeline))

val_dataloader = dict(
    batch_size=32,
    num_workers=4,
    persistent_workers=True,
    pin_memory=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type='ConcatDataset', datasets=val_list, pipeline=test_pipeline))

test_dataloader = dict(
    batch_size=32,
    num_workers=4,
    persistent_workers=True,
    pin_memory=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type='ConcatDataset', datasets=test_list, pipeline=test_pipeline))

val_evaluator = dict(_delete_=True, type='OneMinusNEDMetric')
test_evaluator = dict(_delete_=True, type='OneMinusNEDMetric')

work_dir = 'work_dirs/mthv2_svtr_large_k3_full_gpu1'
