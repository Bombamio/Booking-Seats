import warnings

warnings.filterwarnings(
    'ignore',
    message='Field name .* shadows an attribute in parent',
    category=UserWarning,
)
