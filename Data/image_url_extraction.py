import re
import pandas as pd

INPUT_CSV = "fra_cleaned.csv"
OUTPUT_CSV = "fra_cleaned_with_images.csv"


def load_csv(path):
    df = pd.read_csv(
        path,
        sep=";",
        encoding="latin1",
        engine="python",
        decimal=","
    )
    df.columns = [col.strip().lower() for col in df.columns]
    return df


def build_image_url(fragrantica_url):
    if not isinstance(fragrantica_url, str):
        return None

    match = re.search(r'-(\d+)\.html$', fragrantica_url.strip())
    if not match:
        return None

    perfume_id = match.group(1)
    return f"https://fimgs.net/mdimg/perfume-thumbs/375x500.{perfume_id}.jpg"


def main():
    df = load_csv(INPUT_CSV)
    df["image_url"] = df["url"].apply(build_image_url)
    df.to_csv(OUTPUT_CSV, sep=";", index=False, encoding="utf-8-sig")
    print(f"Done. Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()