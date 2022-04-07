# conditional-nft-generator

Python module to generate NFTs based on conditions and categories of different layers

## Requirements

- Python3.X +
- Pillow
- Numpy

```
pip install -r requirements.txt
```

## Setup

Create folders for proper works

```
mkdir images
mkdir layers
mkdir metadatas
```

And then place your Layers in the Layer folder on each folder name as attribute and build your config.json file : 
```
nft_generator
│
└───layers
│   │
│   └───attribut1
│   │   │   attr1A.png
│   │   │   attr1A.png
│   │   │   ...
│   └───attribut2
│       │   attr1A.png
│       │   attr1A.png
│       │   ...
│ 
└───config.json
```

## Config File

Before running your NFT Generation, you need to build your config file regarding your needs. The file is read and for each object in the layers list, random values are selected and checked for uniqueness against all previously generated metadata files.
You also have possibility to define incompatibility rules (Attribute A will never be matched with Attribute B). You can also clusterize your collection by organizing your file with a specific nomenclature : Imagine you have certain type of background, if Background A is chosen, then you can say I want a specific prefix on another attribute to be chosen.

```
{
    "layers": [
            {
                "name": "Background",
                "values": ["A_Blue", "B_Red", "C_Green"],
                "trait_path": "./layers/Backgrounds",
                "filename": ["A_BLUE", "B_RED", "C_GREEN"], #BLUE.png, ...
                "weights": [30, 45, 15] # Rarity
            },
            {
                "name": "Accessory",
                "values": ["Accessory 1"],
                "trait_path": "./layers/Accessory",
                "filename": ["ACCESSORY1"],
                "layer_nb": 1,
                "weights": [100]
            },
            {
                "name": "Person",
                "values": ["Person 1", "Person 2", "Person 3"],
                "trait_path": "./layers/Person",
                "filename": ["A_PERSON1", "B_PERSON2", "C_PERSON3"],
                "layer_nb": 1,
                "weights": [33,33,33]
            },
        ...
    ],
    "conditions": [
            {
                "layer": "Background",
                "value": "Green",
                "incompatible_with": ["Accessory 1"]
            }
    ],
    "cluster": [
            {
                "guidance_layer": "Background",
                "targetted_layers" : "Person"  #Background will be clusterized with Person
            }
    ],
    "baseURI": ".",
    "name": "NFT #",
    "description": "This is a description for this NFT series."
}
```


## Generate your nft

```
$ python main.py --nb_generation 100 --dimension 1000 1000
```