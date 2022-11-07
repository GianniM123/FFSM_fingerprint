familys=$(ls -d */)

mvn -f ../equivalence-checker/equivalence/pom.xml compile
for family in $familys
do
    cd $family
    mkdir -p combined

    files=($(find *.dot))
    first_file=${files[0]}
    unset files[0]
    output_file="combined/${family:0:-1}-distinct.dot"
    cp $first_file $output_file

    combined=($first_file)
    
    for file in ${files[@]}
    do
        same=false
        for added_file in ${combined[@]}
        do
            output=$(mvn -f ../../equivalence-checker/equivalence/pom.xml exec:java -D exec.mainClass=com.thesis.checker.App -D exec.args="${file} ${added_file}" | grep true)
            if [ "$output" = "true" ]; then
                same=true
                break
            fi
        done
        
        if [ "$same" = "false" ]; then
            combined=(${combined[@]} $file)
            python3 ../../FFSM_diff/algorithm/main.py --ref=$output_file --upd=$file -o $output_file -s yices
        fi

    done

    echo $family
    cd ../

done