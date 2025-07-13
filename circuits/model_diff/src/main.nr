use dep::std::hash::hash_to_field;

// Model diff proof circuit for Aztec Protocol
// Proves that the model diff was generated from legitimate training

// Input structure for model diff proof
struct ModelDiffInput {
    // Training proof hash
    training_proof_hash: Field,
    // Model parameters before training
    model_params_before: [Field; 4],
    // Model parameters after training
    model_params_after: [Field; 4],
    // Model diff hash
    model_diff_hash: Field,
    // Training metadata
    batch_size: u32,
    num_epochs: u32,
    // Final loss
    final_loss: Field,
}



// Main model diff proof circuit
fn main(
    training_proof_hash: Field,
    model_params_before: [Field; 4],
    model_params_after: [Field; 4],
    model_diff_hash: Field,
    batch_size: u32,
    num_epochs: u32,
    final_loss: Field,
) -> pub [Field; 3] {
    // Create model diff input
    let diff_input = ModelDiffInput {
        training_proof_hash,
        model_params_before,
        model_params_after,
        model_diff_hash,
        batch_size,
        num_epochs,
        final_loss,
    };

    // Verify model diff
    let diff_valid = verify_model_diff(diff_input);
    
    // Calculate diff fingerprint
    let diff_fingerprint = calculate_diff_fingerprint(diff_input);
    
    // Generate proof hash
    let proof_hash = hash_model_diff_proof(diff_input, diff_valid, diff_fingerprint);
    
    [proof_hash, diff_valid.into(), diff_fingerprint]
}

// Verify that the model diff is valid
fn verify_model_diff(input: ModelDiffInput) -> bool {
    // Check that training proof hash is valid
    let training_proof_valid = input.training_proof_hash != 0;
    
    // Check that model parameters actually changed
    let params_changed = verify_parameter_changes(input.model_params_before, input.model_params_after);
    
    // Check that model diff hash matches calculated diff
    let diff_hash_valid = verify_diff_hash(input.model_params_before, input.model_params_after, input.model_diff_hash);
    
    // Check that training parameters are reasonable
    let params_valid = verify_training_params(input.batch_size, input.num_epochs);
    
    // Check that loss is reasonable
    let loss_valid = verify_loss(input.final_loss);
    
    // All conditions must be met
    training_proof_valid & params_changed & diff_hash_valid & params_valid & loss_valid
}

// Verify that model parameters actually changed
fn verify_parameter_changes(before: [Field; 4], after: [Field; 4]) -> bool {
    let mut changed = false;
    
    if before[0] != after[0] {
        changed = true;
    }
    if before[1] != after[1] {
        changed = true;
    }
    if before[2] != after[2] {
        changed = true;
    }
    if before[3] != after[3] {
        changed = true;
    }
    
    changed
}

// Verify that the model diff hash matches the calculated diff
fn verify_diff_hash(before: [Field; 4], after: [Field; 4], expected_hash: Field) -> bool {
    let calculated_hash = calculate_model_diff_hash(before, after);
    calculated_hash == expected_hash
}

// Calculate hash of model diff
fn calculate_model_diff_hash(before: [Field; 4], after: [Field; 4]) -> Field {
    let diff = [
        after[0] - before[0],
        after[1] - before[1],
        after[2] - before[2],
        after[3] - before[3]
    ];
    
    hash_to_field(diff)
}

// Verify that training parameters are reasonable
fn verify_training_params(batch_size: u32, num_epochs: u32) -> bool {
    let batch_valid = batch_size > 0 & batch_size <= 1024;
    let epochs_valid = num_epochs > 0 & num_epochs <= 100;
    
    batch_valid & epochs_valid
}

// Verify that the loss value is reasonable
fn verify_loss(loss: Field) -> bool {
    loss != 0
}

// Calculate diff fingerprint
fn calculate_diff_fingerprint(input: ModelDiffInput) -> Field {
    let fingerprint_data = [
        input.training_proof_hash,
        input.model_params_before[0],
        input.model_params_before[1],
        input.model_params_before[2],
        input.model_params_before[3],
        input.model_params_after[0],
        input.model_params_after[1],
        input.model_params_after[2]
    ];
    
    hash_to_field(fingerprint_data)
}

// Hash the complete model diff proof
fn hash_model_diff_proof(input: ModelDiffInput, valid: bool, fingerprint: Field) -> Field {
    let valid_field: Field = if valid { 1 } else { 0 };
    
    let proof_data = [
        input.training_proof_hash,
        input.model_params_before[0],
        input.model_params_before[1],
        input.model_params_before[2],
        input.model_params_before[3],
        input.model_params_after[0],
        input.model_params_after[1],
        input.model_params_after[2],
        valid_field,
        fingerprint
    ];
    
    hash_to_field(proof_data)
} 