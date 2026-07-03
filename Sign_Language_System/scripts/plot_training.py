import matplotlib # type: ignore
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

os.makedirs('results', exist_ok=True)

# Manually enter your training history from the terminal output
history = {
    'accuracy':     [0.8641, 0.9344, 0.9447, 0.9520, 0.9603, 0.9641, 0.9648, 0.9603],
    'val_accuracy': [0.8036, 0.8076, 0.7971, 0.7982, 0.8202, 0.8159, 0.7999, 0.8173],
    'loss':         [0.4449, 0.1968, 0.1660, 0.1451, 0.1194, 0.1080, 0.1070, 0.1287],
    'val_loss':     [0.6451, 0.7012, 0.7324, 0.7806, 0.7849, 0.7956, 0.9371, 0.7507],
}
epochs = range(1, len(history['accuracy']) + 1)

# Accuracy curve
plt.figure(figsize=(10, 5))
plt.plot(epochs, [v*100 for v in history['accuracy']], 'b-o', label='Training Accuracy')
plt.plot(epochs, [v*100 for v in history['val_accuracy']], 'r-o', label='Validation Accuracy')
plt.axvline(x=5, color='green', linestyle='--', label='Best Checkpoint (Epoch 5)')
plt.title('Training and Validation Accuracy', fontsize=14, fontweight='bold')
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Accuracy (%)', fontsize=12)
plt.xticks(epochs)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/accuracy_curve.png', dpi=150)
plt.close()
print("Saved → results/accuracy_curve.png")

# Loss curve
plt.figure(figsize=(10, 5))
plt.plot(epochs, history['loss'], 'b-o', label='Training Loss')
plt.plot(epochs, history['val_loss'], 'r-o', label='Validation Loss')
plt.axvline(x=5, color='green', linestyle='--', label='Best Checkpoint (Epoch 5)')
plt.title('Training and Validation Loss', fontsize=14, fontweight='bold')
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Loss', fontsize=12)
plt.xticks(epochs)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/loss_curve.png', dpi=150)
plt.close()
print("Saved → results/loss_curve.png")

print("Done!")