docker run -it --rm binster bash -c "lz4cat /var/lib/apt/lists/*.lz4 | grep ^Filename | grep dbgsym" |
	awk '{print $2}' | sed -e "s|.*/main/||" > /tmp/pkgs-$$
fromdos /tmp/pkgs-$$

cat /tmp/pkgs-$$ | xargs -d'\n' basename -a | sed -e "s/-dbgsym.*_/-/" -e "s/^/#/" > /tmp/names-$$
paste /tmp/pkgs-$$ /tmp/names-$$ | sed -e "s|^|./download.sh |" | tr '\t' ' '
