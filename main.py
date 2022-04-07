from PIL import Image
import random
import json
import os
import numpy as np
import argparse
from tqdm import tqdm

def build_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))


def create_new_image(all_images, config):
    """
    Create Image based on provided config file
    """
    new_image = {}
    mapped_cluster = build_dict(config["cluster"], key="targetted_layers")

    for layer in config["layers"]:
        current_cluster = mapped_cluster.get(layer["name"])
        if current_cluster:
            prefix = new_image[current_cluster["guidance_layer"]].split('_')[0]
            retained_idxs = [i for i in range(len(layer['filename'])) if prefix+"_" in layer['filename'][i]]
            retained_idxs_any = [i for i in range(len(layer['filename'])) if "_" not in layer['filename'][i]]
            layer_choices = np.take(layer['values'], retained_idxs_any + retained_idxs)
            weights_choices = np.take(layer['weights'], retained_idxs_any + retained_idxs)
            new_image[layer["name"]] = random.choices(layer_choices, weights_choices)[0]
        else:
            new_image[layer["name"]] = random.choices(layer["values"], layer["weights"])[0]
    
    for incomp in config["conditions"]:
        for attr in new_image:
            if new_image[incomp["layer"]] == incomp["value"] and new_image[attr] in incomp["incompatible_with"]:
                return create_new_image(all_images, config)

    if new_image in all_images:
        return create_new_image(all_images, config)
    else:
        return new_image


def generate_unique_images(amount, dimension=(1000,1000)):
    f = open('config.json')
    config = json.load(f)
    config["layers"] = sorted(config["layers"], key=lambda d: d['layer_nb']) 
    padding = len(str(amount))
    trait_files = {
    }
    for trait in config["layers"]:
        trait_files[trait["name"]] = {}
        for x, key in enumerate(trait["values"]):
            trait_files[trait["name"]][key] = trait["filename"][x]
    print(trait_files)
    all_images = []
    for i in range(amount): 
        new_trait_image = create_new_image(all_images, config)
        all_images.append(new_trait_image)
    i = 1
    for item in all_images:
        item["tokenId"] = i
        i += 1

        
    for i, token in enumerate(all_images):
        attributes = []
        for key in token:
            if key != "tokenId":
                attributes.append({"trait_type": key, "value": token[key]})
            token_metadata = {
                "image": config["baseURI"] + "/images/" + str(token["tokenId"]) + '.png',
                "tokenId": token["tokenId"],
                "name":  config["name"] + str(token["tokenId"]).zfill(padding),
                "description": config["description"],
                "attributes": attributes
            }
        with open('./metadata/' + str(token["tokenId"]) + '.json', 'w') as outfile:
            json.dump(token_metadata, outfile, indent=4)

    with open('./metadata/collection.json', 'w') as outfile:
        json.dump(all_images, outfile, indent=4)
  
    for item in tqdm(all_images):
        layers = []
        for index, attr in enumerate(item):
            if attr != 'tokenId':
                layers.append([])
                layers[index] = Image.open(f'{config["layers"][index]["trait_path"]}/{trait_files[attr][item[attr]]}.png').convert('RGBA').resize(dimension)
        if len(layers) == 1:
            rgb_im = layers[0].convert('RGBA')
            file_name = str(item["tokenId"]) + ".png"
            rgb_im.save("./images/" + file_name)
        elif len(layers) == 2:
            main_composite = Image.alpha_composite(layers[0], layers[1])
            rgb_im = main_composite.convert('RGBA')
            file_name = str(item["tokenId"]) + ".png"
            rgb_im.save("./images/" + file_name)
        elif len(layers) >= 3:
            main_composite = Image.alpha_composite(layers[0], layers[1])
            layers.pop(0)
            layers.pop(0)
            for index, remaining in enumerate(layers):
                main_composite = Image.alpha_composite(main_composite, remaining)
            rgb_im = main_composite.convert('RGBA')
            file_name = str(item["tokenId"]) + ".png"
            rgb_im.save("./images/" + file_name)

    print("\nNFTs has been generated. Enter IPFS CID")
    cid = input("IPFS CID (): ")
    if len(cid) > 0:
        if not cid.startswith("ipfs://"):
            cid = "ipfs://{}".format(cid)
        if cid.endswith("/"):
            cid = cid[:-1]
        for i, item in enumerate(all_images):
            with open('./metadata/' + str(item["tokenId"]) + '.json', 'r') as infile:
                original_json = json.loads(infile.read())
                original_json["image"] = original_json["image"].replace(config["baseURI"]+"/", cid+"/")
                with open('./metadata/' + str(item["tokenId"]) + '.json', 'w') as outfile:
                    json.dump(original_json, outfile, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--nb_generation', help="Number of NFTs to generate.", type=int)
    parser.add_argument(
        '--dimension', help="(a,b) Dimension of the NFTs.", nargs='+', type=int, default=(1000,1000))
    args = parser.parse_args()
    generate_unique_images(args.nb_generation, tuple(args.dimension))