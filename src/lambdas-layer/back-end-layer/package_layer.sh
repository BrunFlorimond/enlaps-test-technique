rm -rf ./python ./layer.zip

for dir in model services constants; do
    mkdir -p python/src/$dir
    rsync -av --include='*/' --include='*.py' --exclude='*' ../../$dir/ ./python/src/$dir/
done
mkdir -p ./python/cloudformation/dynamodb
cp ../../../cloudformation/dynamodb/dynamodb-setup.yaml ./python/cloudformation/dynamodb/dynamodb-setup.yaml
cp -r back-end-layer/lib python/
zip -r layer.zip python