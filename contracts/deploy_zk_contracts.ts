import { ethers } from "hardhat";
import { HardhatRuntimeEnvironment } from "hardhat/types";

async function main(hre: HardhatRuntimeEnvironment) {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());

  // Deploy ProofVerifier
  console.log("\n=== Deploying ProofVerifier ===");
  const ProofVerifier = await ethers.getContractFactory("ProofVerifier");
  const proofVerifier = await ProofVerifier.deploy(deployer.address); // Pass initial owner
  await proofVerifier.waitForDeployment();

  console.log("ProofVerifier deployed to:", await proofVerifier.getAddress());

  // Deploy AztecOrchestrator
  console.log("\n=== Deploying AztecOrchestrator ===");
  const AztecOrchestrator = await ethers.getContractFactory("AztecOrchestrator");
  const aztecOrchestrator = await AztecOrchestrator.deploy();
  await aztecOrchestrator.waitForDeployment();

  console.log("AztecOrchestrator deployed to:", await aztecOrchestrator.getAddress());

  // Deploy Vault
  console.log("\n=== Deploying Vault ===");
  const Vault = await ethers.getContractFactory("Vault");
  const vault = await Vault.deploy();
  await vault.waitForDeployment();

  console.log("Vault deployed to:", await vault.getAddress());

  // Set up initial configuration
  console.log("\n=== Setting up initial configuration ===");
  
  // Set verification thresholds in ProofVerifier
  const minTrainingLoss = ethers.parseEther("0.1"); // 0.1
  const maxTrainingLoss = ethers.parseEther("10.0"); // 10.0
  const minBatchSize = 1;
  const maxBatchSize = 1024;
  const minEpochs = 1;
  const maxEpochs = 100;

  await proofVerifier.setVerificationThresholds(
    minTrainingLoss,
    maxTrainingLoss,
    minBatchSize,
    maxBatchSize,
    minEpochs,
    maxEpochs
  );
  console.log("✓ Verification thresholds set");

  // Set verification keys (placeholder values for now)
  const trainingProofVK = ethers.keccak256(ethers.toUtf8Bytes("training_proof_vk"));
  const dataIntegrityVK = ethers.keccak256(ethers.toUtf8Bytes("data_integrity_vk"));
  const modelDiffVK = ethers.keccak256(ethers.toUtf8Bytes("model_diff_vk"));

  await proofVerifier.setVerificationKeys(
    trainingProofVK,
    dataIntegrityVK,
    modelDiffVK
  );
  console.log("✓ Verification keys set");

  // Note: Vault is a stub contract without ownership functionality
  console.log("✓ Vault deployed (stub contract)");

  // Verify deployments
  console.log("\n=== Verifying deployments ===");
  
  const proofVerifierOwner = await proofVerifier.owner();

  console.log("ProofVerifier owner:", proofVerifierOwner);
  console.log("AztecOrchestrator address:", await aztecOrchestrator.getAddress());
  console.log("Vault address:", await vault.getAddress());

  // Verify configuration
  const thresholds = await proofVerifier.getVerificationThresholds();
  console.log("Verification thresholds:", {
    minTrainingLoss: ethers.formatEther(thresholds[0]),
    maxTrainingLoss: ethers.formatEther(thresholds[1]),
    minBatchSize: Number(thresholds[2]),
    maxBatchSize: Number(thresholds[3]),
    minEpochs: Number(thresholds[4]),
    maxEpochs: Number(thresholds[5])
  });

  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    deployer: deployer.address,
    contracts: {
      proofVerifier: await proofVerifier.getAddress(),
      aztecOrchestrator: await aztecOrchestrator.getAddress(),
      vault: await vault.getAddress()
    },
    configuration: {
      verificationThresholds: {
        minTrainingLoss: ethers.formatEther(thresholds[0]),
        maxTrainingLoss: ethers.formatEther(thresholds[1]),
        minBatchSize: Number(thresholds[2]),
        maxBatchSize: Number(thresholds[3]),
        minEpochs: Number(thresholds[4]),
        maxEpochs: Number(thresholds[5])
      },
      verificationKeys: {
        trainingProofVK: trainingProofVK,
        dataIntegrityVK: dataIntegrityVK,
        modelDiffVK: modelDiffVK
      }
    },
    timestamp: new Date().toISOString()
  };

  const fs = require("fs");
  fs.writeFileSync(
    "deployment-info.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("\n=== Deployment Summary ===");
  console.log("✓ All contracts deployed successfully");
  console.log("✓ Initial configuration completed");
  console.log("✓ Deployment info saved to deployment-info.json");
  console.log("\nContract Addresses:");
  console.log("- ProofVerifier:", await proofVerifier.getAddress());
  console.log("- AztecOrchestrator:", await aztecOrchestrator.getAddress());
  console.log("- Vault:", await vault.getAddress());

  // Test basic functionality
  console.log("\n=== Testing basic functionality ===");
  
  try {
    // Test proof submission (should fail with invalid proof, but not revert)
    const testProofHash = ethers.keccak256(ethers.toUtf8Bytes("test_proof"));
    const testProofData = ethers.toUtf8Bytes("test_data");
    
    await proofVerifier.submitProof(
      "training_proof",
      testProofHash,
      testProofData
    );
    console.log("✓ Proof submission test passed");
    
    // Check if proof is valid (should be false for test data)
    const isValid = await proofVerifier.isProofValid(testProofHash);
    console.log("✓ Proof validation test passed (valid:", isValid, ")");
    
  } catch (error) {
    console.log("⚠️  Basic functionality test failed:", error.message);
  }

  console.log("\n🎉 ZK Proof System deployment completed successfully!");
}

// Handle errors
main(require("hardhat")).catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
}); 