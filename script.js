const uploadImage = document.getElementById("uploadImage");
const convertButton = document.getElementById("convertButton");
const originalCanvas = document.getElementById("originalCanvas");
const sketchCanvas = document.getElementById("sketchCanvas");
const originalCtx = originalCanvas.getContext("2d");
const sketchCtx = sketchCanvas.getContext("2d");

let originalImage = null;

// Load the uploaded image onto the original canvas
uploadImage.addEventListener("change", function (event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const img = new Image();
      img.onload = function () {
        originalCanvas.width = img.width;
        originalCanvas.height = img.height;
        sketchCanvas.width = img.width;
        sketchCanvas.height = img.height;
        originalCtx.drawImage(img, 0, 0);
        originalImage = img;
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
});

// Convert the image to a sketch
convertButton.addEventListener("click", function () {
  if (!originalImage) {
    alert("Please upload an image first.");
    return;
  }

  // Step 1: Convert to Grayscale
  const imageData = originalCtx.getImageData(0, 0, originalCanvas.width, originalCanvas.height);
  const pixels = imageData.data;

  for (let i = 0; i < pixels.length; i += 4) {
    const r = pixels[i];
    const g = pixels[i + 1];
    const b = pixels[i + 2];

    // Grayscale formula: Y = 0.299*R + 0.587*G + 0.114*B
    const grayscale = 0.299 * r + 0.587 * g + 0.114 * b;

    pixels[i] = grayscale; // Red channel
    pixels[i + 1] = grayscale; // Green channel
    pixels[i + 2] = grayscale; // Blue channel
  }

  // Update canvas with grayscale image
  sketchCtx.putImageData(imageData, 0, 0);

  // Step 2: Invert the image
  for (let i = 0; i < pixels.length; i += 4) {
    pixels[i] = 255 - pixels[i]; // Invert Red channel
    pixels[i + 1] = 255 - pixels[i + 1]; // Invert Green channel
    pixels[i + 2] = 255 - pixels[i + 2]; // Invert Blue channel
  }

  // Update canvas with inverted image
  sketchCtx.putImageData(imageData, 0, 0);

  // Step 3: Blur the inverted image (Simple Gaussian Blur Approximation)
  const blurredData = blurImage(imageData, originalCanvas.width, originalCanvas.height);

  // Step 4: Dodge blend the original grayscale with the blurred inverted image
  const finalPixels = imageData.data;
  const blurredPixels = blurredData.data; // Use the data property of the blurred image
  for (let i = 0; i < pixels.length; i += 4) {
    finalPixels[i] = dodge(blurredPixels[i], finalPixels[i]);
    finalPixels[i + 1] = dodge(blurredPixels[i + 1], finalPixels[i + 1]);
    finalPixels[i + 2] = dodge(blurredPixels[i + 2], finalPixels[i + 2]);
  }

  // Display the final sketch
  sketchCtx.putImageData(imageData, 0, 0);
});

// Helper function for Dodge Blend
function dodge(blurValue, grayValue) {
  return Math.min(255, (blurValue * 255) / (255 - grayValue));
}

// Simple Gaussian Blur Approximation
function blurImage(imageData, width, height) {
  const blurred = new ImageData(width, height);
  const kernel = [1, 4, 6, 4, 1]; // Gaussian kernel
  const kernelSum = kernel.reduce((a, b) => a + b, 0);

  // Apply kernel horizontally and vertically
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      let r = 0, g = 0, b = 0;

      // Apply kernel horizontally
      for (let k = -2; k <= 2; k++) {
        const xk = x + k;
        if (xk >= 0 && xk < width) {
          const idx = (y * width + xk) * 4;
          const weight = kernel[k + 2];
          r += imageData.data[idx] * weight;
          g += imageData.data[idx + 1] * weight;
          b += imageData.data[idx + 2] * weight;
        }
      }

      // Normalize
      const idx = (y * width + x) * 4;
      blurred.data[idx] = r / kernelSum;
      blurred.data[idx + 1] = g / kernelSum;
      blurred.data[idx + 2] = b / kernelSum;
    }
  }

  // Apply kernel vertically
  const tempData = new Uint8ClampedArray(blurred.data);
  for (let x = 0; x < width; x++) {
    for (let y = 0; y < height; y++) {
      let r = 0, g = 0, b = 0;

      // Apply kernel vertically
      for (let k = -2; k <= 2; k++) {
        const yk = y + k;
        if (yk >= 0 && yk < height) {
          const idx = (yk * width + x) * 4;
          const weight = kernel[k + 2];
          r += tempData[idx] * weight;
          g += tempData[idx + 1] * weight;
          b += tempData[idx + 2] * weight;
        }
      }

      // Normalize
      const idx = (y * width + x) * 4;
      blurred.data[idx] = r / kernelSum;
      blurred.data[idx + 1] = g / kernelSum;
      blurred.data[idx + 2] = b / kernelSum;
    }
  }

  return blurred;
}
