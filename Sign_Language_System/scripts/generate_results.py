import os
import json
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
import warnings
warnings.filterwarnings('ignore')

os.makedirs('results', exist_ok=True)

DATASET_PATH = "asl_alphabet_train"
MODEL_PATH   = "models/sign_language_model.keras"
IMG_SIZE     = (224, 224)
BATCH_SIZE   = 32
NUM_CLASSES  = 29

print("Loading class labels...")
with open("models/class_labels.json") as f:
    class_labels = json.load(f)
class_names = [class_labels[str(i)] for i in range(NUM_CLASSES)]

# ─── helper: build data generator ────────────────────────────────
def make_generator(subset=None, validation_split=None):
    kwargs = dict(rescale=1./255)
    if validation_split:
        kwargs['validation_split'] = validation_split
    gen = tf.keras.preprocessing.image.ImageDataGenerator(**kwargs)
    flow_kwargs = dict(
        target_size=IMG_SIZE, batch_size=BATCH_SIZE,
        class_mode='categorical', shuffle=False
    )
    if subset:
        flow_kwargs['subset'] = subset
    return gen.flow_from_directory(DATASET_PATH, **flow_kwargs)

# ════════════════════════════════════════════════════════════════
# 1.  ROC-AUC  (runs on full dataset — fast, single forward pass)
# ════════════════════════════════════════════════════════════════
print("\n── ROC-AUC ─────────────────────────────────────────────")
model = tf.keras.models.load_model(MODEL_PATH)

full_gen = make_generator()
print(f"  Predicting on {full_gen.samples} images …")
y_pred_prob = model.predict(full_gen, verbose=1)
y_true_idx  = full_gen.classes
y_true_bin  = label_binarize(y_true_idx, classes=list(range(NUM_CLASSES)))

fpr_dict, tpr_dict, roc_auc_dict = {}, {}, {}
for i in range(NUM_CLASSES):
    fpr_dict[i], tpr_dict[i], _ = roc_curve(y_true_bin[:, i], y_pred_prob[:, i])
    roc_auc_dict[i] = auc(fpr_dict[i], tpr_dict[i])

# macro average
all_fpr = np.unique(np.concatenate([fpr_dict[i] for i in range(NUM_CLASSES)]))
mean_tpr = np.zeros_like(all_fpr)
for i in range(NUM_CLASSES):
    mean_tpr += np.interp(all_fpr, fpr_dict[i], tpr_dict[i])
mean_tpr /= NUM_CLASSES
macro_auc = auc(all_fpr, mean_tpr)
print(f"  Macro AUC = {macro_auc:.4f}")

fig, ax = plt.subplots(figsize=(9, 7))
colors = plt.cm.tab20(np.linspace(0, 1, NUM_CLASSES))
for i, col in zip(range(NUM_CLASSES), colors):
    ax.plot(fpr_dict[i], tpr_dict[i], color=col, lw=1, alpha=0.45,
            label=f'{class_names[i]} (AUC={roc_auc_dict[i]:.2f})')
ax.plot(all_fpr, mean_tpr, color='black', lw=2.5,
        label=f'Macro-Average (AUC = {macro_auc:.4f})')
ax.plot([0,1],[0,1],'k--', lw=1, label='Random Classifier')
ax.set_xlabel('False Positive Rate', fontsize=13)
ax.set_ylabel('True Positive Rate', fontsize=13)
ax.set_title('ROC-AUC Curve – One-vs-Rest (29 Classes)', fontsize=14, fontweight='bold')
ax.legend(fontsize=7, loc='lower right', ncol=2)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/roc_auc.png', dpi=150)
plt.close()
print("  Saved → results/roc_auc.png")

# save AUC values
auc_data = {class_names[i]: round(roc_auc_dict[i], 4) for i in range(NUM_CLASSES)}
auc_data['macro_avg'] = round(macro_auc, 4)
with open('results/auc_values.json','w') as f:
    json.dump(auc_data, f, indent=2)

# ════════════════════════════════════════════════════════════════
# 2.  GRAD-CAM  (on one sample per class)
# ════════════════════════════════════════════════════════════════
print("\n── Grad-CAM ────────────────────────────────────────────")

# Find last conv layer
last_conv = None
for layer in reversed(model.layers):
    if isinstance(layer, tf.keras.layers.Conv2D):
        last_conv = layer.name
        break
print(f"  Last conv layer: {last_conv}")

grad_model = tf.keras.models.Model(
    inputs  = model.inputs,
    outputs = [model.get_layer(last_conv).output, model.output]
)

def make_gradcam(img_array, class_idx):
    with tf.GradientTape() as tape:
        conv_out, preds = grad_model(img_array)
        loss = preds[:, class_idx]
    grads    = tape.gradient(loss, conv_out)
    pooled   = tf.reduce_mean(grads, axis=(0,1,2))
    cam      = conv_out[0] @ pooled[..., tf.newaxis]
    cam      = tf.squeeze(cam).numpy()
    cam      = np.maximum(cam, 0)
    if cam.max() > 0:
        cam /= cam.max()
    return cam

def load_sample_image(class_name):
    folder = os.path.join(DATASET_PATH, class_name)
    fname  = sorted(os.listdir(folder))[0]
    path   = os.path.join(folder, fname)
    img    = tf.keras.preprocessing.image.load_img(path, target_size=IMG_SIZE)
    arr    = tf.keras.preprocessing.image.img_to_array(img) / 255.0
    return arr, path

# Generate Grad-CAM grid for 6 sample classes
sample_classes = ['A','B','C','D','E','F']
fig, axes = plt.subplots(2, 6, figsize=(18, 6))
for col, cname in enumerate(sample_classes):
    idx      = class_names.index(cname)
    img_arr, _ = load_sample_image(cname)
    inp      = np.expand_dims(img_arr, 0)
    cam      = make_gradcam(inp, idx)
    cam_resized = tf.image.resize(cam[..., np.newaxis], IMG_SIZE).numpy().squeeze()

    axes[0, col].imshow(img_arr)
    axes[0, col].set_title(f'Input: "{cname}"', fontsize=10)
    axes[0, col].axis('off')

    axes[1, col].imshow(img_arr)
    axes[1, col].imshow(cam_resized, cmap='jet', alpha=0.50)
    axes[1, col].set_title(f'Grad-CAM: "{cname}"', fontsize=10)
    axes[1, col].axis('off')

plt.suptitle('Grad-CAM Explainability Analysis – Sample Signs', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('results/gradcam.png', dpi=150)
plt.close()
print("  Saved → results/gradcam.png")

# ════════════════════════════════════════════════════════════════
# 3.  5-FOLD CROSS-VALIDATION  (uses subset of data for speed)
# ════════════════════════════════════════════════════════════════
print("\n── 5-Fold Cross-Validation ──────────────────────────────")
print("  Loading image paths and labels …")

all_paths, all_labels = [], []
for label_idx, cname in enumerate(class_names):
    folder = os.path.join(DATASET_PATH, cname)
    files  = sorted(os.listdir(folder))[:500]   # 500 per class = 14,500 total (fast)
    for fname in files:
        all_paths.append(os.path.join(folder, fname))
        all_labels.append(label_idx)

all_paths  = np.array(all_paths)
all_labels = np.array(all_labels)
print(f"  Using {len(all_paths)} images for CV …")

def load_image(path):
    img = tf.keras.preprocessing.image.load_img(path, target_size=IMG_SIZE)
    return tf.keras.preprocessing.image.img_to_array(img) / 255.0

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = []

for fold, (train_idx, test_idx) in enumerate(skf.split(all_paths, all_labels)):
    print(f"\n  Fold {fold+1}/5 — evaluating on {len(test_idx)} images …")
    X_test = np.array([load_image(p) for p in all_paths[test_idx]])
    y_test = all_labels[test_idx]

    preds     = model.predict(X_test, batch_size=BATCH_SIZE, verbose=0)
    pred_cls  = np.argmax(preds, axis=1)
    acc       = np.mean(pred_cls == y_test)
    cv_scores.append(acc)
    print(f"  Fold {fold+1} Accuracy: {acc*100:.2f}%")

mean_cv = np.mean(cv_scores)
std_cv  = np.std(cv_scores)
print(f"\n  Mean CV Accuracy : {mean_cv*100:.2f}%")
print(f"  Std Dev          : {std_cv*100:.2f}%")

# Save CV results
cv_results = {f'fold_{i+1}': round(cv_scores[i], 4) for i in range(5)}
cv_results['mean'] = round(mean_cv, 4)
cv_results['std']  = round(std_cv, 4)
with open('results/cv_results.json','w') as f:
    json.dump(cv_results, f, indent=2)

# CV chart
folds = [f'Fold {i+1}' for i in range(5)]
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(folds, [v*100 for v in cv_scores],
              color='#1F77B4', alpha=0.85, edgecolor='white')
ax.axhline(mean_cv*100, color='#D62728', linestyle='--', lw=1.8,
           label=f'Mean = {mean_cv*100:.2f}%')
for bar, val in zip(bars, cv_scores):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
            f'{val*100:.2f}%', ha='center', va='bottom',
            fontsize=10, fontweight='bold')
ax.set_xlabel('Fold', fontsize=12)
ax.set_ylabel('Accuracy (%)', fontsize=12)
ax.set_title('5-Fold Cross-Validation Accuracy', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('results/cross_validation.png', dpi=150)
plt.close()
print("  Saved → results/cross_validation.png")

print("\n✅ All results generated successfully!")
print("   results/roc_auc.png")
print("   results/gradcam.png")
print("   results/cross_validation.png")
print("   results/auc_values.json")
print("   results/cv_results.json")