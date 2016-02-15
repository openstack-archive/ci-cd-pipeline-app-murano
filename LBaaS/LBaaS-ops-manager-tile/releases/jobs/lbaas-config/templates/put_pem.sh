host=$1
pem_file=$2
pkey_path=$3

echo $host
echo $pem_file
echo $pkey_path

scp -o StrictHostKeyChecking=no -i $pkey_path $pem_file ec2-user@$host:~/

ssh -o StrictHostKeyChecking=no -i $pkey_path ec2-user@$host "sudo mv ~/cf.pem /etc/ssl/"