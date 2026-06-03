_base_ = ['/home/ubuntu/mmocr/configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py']

work_dir = 'work_dirs/mthv2_sar_k3_full_gpu1'

train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=30, val_interval=1)

train_pipeline = [
    dict(type='LoadImageFromFile', ignore_empty=True, min_size=2),
    dict(
        type='ConditionApply',
        true_transforms=[
            dict(
                type='ImgAugWrapper',
                args=[dict(cls='Rot90', k=3, keep_size=False)])
        ],
        condition="results['img_shape'][1] < results['img_shape'][0]"),
    dict(type='LoadOCRAnnotations', with_text=True),
    dict(
        type='RescaleToHeight',
        height=48,
        min_width=48,
        max_width=1024,
        width_divisor=4),
    dict(type='PadToWidth', width=1024),
    dict(
        type='PackTextRecogInputs',
        meta_keys=('img_path', 'ori_shape', 'img_shape', 'valid_ratio')),
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
    dict(
        type='RescaleToHeight',
        height=48,
        min_width=48,
        max_width=1024,
        width_divisor=4),
    dict(type='PadToWidth', width=1024),
    dict(type='LoadOCRAnnotations', with_text=True),
    dict(
        type='PackTextRecogInputs',
        meta_keys=('img_path', 'ori_shape', 'img_shape', 'valid_ratio')),
]

train_dataloader = dict(
    batch_size=16,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        type='ConcatDataset',
        datasets=_base_.train_list,
        pipeline=train_pipeline))

val_dataloader = dict(
    batch_size=16,
    num_workers=8,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type='ConcatDataset',
        datasets=_base_.val_list,
        pipeline=test_pipeline))

test_dataloader = dict(
    batch_size=16,
    num_workers=8,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type='ConcatDataset',
        datasets=_base_.test_list,
        pipeline=test_pipeline))

val_evaluator = dict(_delete_=True, type='OneMinusNEDMetric')
test_evaluator = dict(_delete_=True, type='OneMinusNEDMetric')
