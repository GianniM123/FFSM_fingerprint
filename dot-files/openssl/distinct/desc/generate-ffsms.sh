familys=$(ls -d */)


for family in $familys
do
    cd $family
	cd combined
    files=($(find *.dot))
    file=${files[0]}
	mv $file "../../../../combined/desc/openssl-distinct_${file}"
	cd ..
    cd ..
done