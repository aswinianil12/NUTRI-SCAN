from bing_image_downloader import downloader

# Anemic eyes download cheyyan
downloader.download("anemic conjunctiva eye", limit=50, output_dir='dataset_eye/train/anemic')

# Healthy eyes download cheyyan
downloader.download("healthy human eye conjunctiva", limit=50, output_dir='dataset_eye/train/non_anemic')