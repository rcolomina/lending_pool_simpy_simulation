

node:
	npx hardhat node

deploy:
	npx hardhat run --network localhost scripts/deploy.ts

add-token:	
	npx hardhat run --network localhost scripts/add-token.ts


export-abi:
	npm install --save-dev hardhat-abi-exporter
