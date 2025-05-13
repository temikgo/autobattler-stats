#!/bin/bash

ASSETS_PATH="/home/temikgo/main/MyFiles/media/assets/dev"
OUTPUT_FILE="constants.py"

normalize() {
    echo "${1,,}" | sed 's/ /_/g; s/\.png$//'
}

HEROES=()
for dir in "$ASSETS_PATH/Heroes"/*/; do
    if [ -d "$dir" ]; then
        name=$(basename "$dir")
        norm=$(normalize "$name")
        if [ "$norm" != "ftue" ]; then
            HEROES+=("\"$norm\"")
        fi
    fi
done
IFS=$'\n' HEROES=($(sort <<<"${HEROES[*]}"))

ITEMS=()
while IFS= read -r -d '' file; do
    name=$(basename "$file")
    ITEMS+=("\"$(normalize "$name")\"")
done < <(find "$ASSETS_PATH/Items" -type f -print0)
IFS=$'\n' ITEMS=($(sort <<<"${ITEMS[*]}"))

RELICS=()
for file in "$ASSETS_PATH/Items/Relics"/*; do
    if [ -f "$file" ]; then
        name=$(basename "$file")
        RELICS+=("\"$(normalize "$name")\"")
    fi
done
IFS=$'\n' RELICS=($(sort <<<"${RELICS[*]}"))

{
    echo "HEROES = ["
    printf "    %s,\n" "${HEROES[@]}"
    echo "]"
    echo
    echo "ITEMS = ["
    printf "    %s,\n" "${ITEMS[@]}"
    echo "]"
    echo
    echo "RELICS = ["
    printf "    %s,\n" "${RELICS[@]}"
    echo "]"
} > "$OUTPUT_FILE"

echo "$OUTPUT_FILE successfully generated"
