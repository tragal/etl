from etl.phases import download, extract, transform, load

PIPELINE = [
    ("DOWNLOAD", download.run),
    ("EXTRACT", extract.run),
    ("TRANSFORM", transform.run),
    ("LOAD", load.run),
]
