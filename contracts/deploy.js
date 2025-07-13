// scripts/deploy.js
const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  const AztecOrchestrator = await ethers.getContractFactory("AztecOrchestrator");
  const orchestrator = await AztecOrchestrator.deploy();
  const orchestratorAddress = await orchestrator.getAddress();
  console.log("AztecOrchestrator deployed to:", orchestratorAddress);

  const ProofVerifier = await ethers.getContractFactory("ProofVerifier");
  const verifier = await ProofVerifier.deploy();
  const verifierAddress = await verifier.getAddress();
  console.log("ProofVerifier deployed to:", verifierAddress);

  const Vault = await ethers.getContractFactory("Vault");
  const vault = await Vault.deploy();
  const vaultAddress = await vault.getAddress();
  console.log("Vault deployed to:", vaultAddress);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
}); 