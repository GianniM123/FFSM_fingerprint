familys=$(ls -d */)


for family in $familys
do
    cd $family
    mkdir -p combined

    files=($(find *.dot))
    file=${files[0]}
    unset files[0]
    output="combined/${family:0:-1}.dot"
    cp $file $output 
    for file in ${files[@]}
    do
        python3 ../../FFSM_diff/algorithm/main.py --ref=$output --upd=$file -o $output -s yices
    done
    echo $family
    cd ../ 

done