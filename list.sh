docker run -it --rm binster bash -c "lz4cat /var/lib/apt/lists/*.lz4 | grep Filename | grep dbgsym" | awk '{print $2}' | sed -e "s|.*/main/||" -e "s|^|./download.sh |"
