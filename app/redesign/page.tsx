"use client";
import { useRef, useState, ChangeEvent } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";

export default function RedesignPage() {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [generatedImage, setGeneratedImage] = useState<string>("");
  const [selectedFeature, setSelectedFeature] = useState<string>("");
  const [extraPrompt, setExtraPrompt] = useState<string>("");
  const [textPrompt, setTextPrompt] = useState<string>("");
  const [loading, setLoading] = useState(false);

  // Features for file transformation (retaining the options)
  const transformationFeatures = [
    { value: "color change", label: "Color Change" },
    { value: "refresh", label: "Refresh" },
    { value: "maximize", label: "Maximize" },
    { value: "redesign", label: "Redesign" },
    { value: "functional change", label: "Functional Change" },
    { value: "style stealer", label: "Style Stealer" },
    { value: "image quality enhancer", label: "Image Quality Enhancer" },
  ];

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setSelectedFileName(file.name);
    }
  };

  const handleFeatureSelect = (feature: string) => {
    setSelectedFeature(feature);
  };

  // Existing transformation using an uploaded image.
  const handleApply = async () => {
    if (!imageFile || !selectedFeature) {
      toast({
        title: "Error",
        description: "Please select an image and choose a transformation",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("image", imageFile);
    formData.append("feature", selectedFeature);
    if (extraPrompt) {
      formData.append("extra_prompt", extraPrompt);
    }

    try {
      const response = await fetch("http://localhost:8001/transform", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Image transformation failed");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setGeneratedImage(url);
      toast({
        title: "Success",
        description: "Image generated successfully!",
      });
    } catch (error) {
      console.error(error);
      toast({
        title: "Error",
        description: "Failed to generate image",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // New function for text-to-image generation.
  // This section always uses the default "artistic" feature.
  const handleTextGenerate = async () => {
    if (!textPrompt) {
      toast({
        title: "Error",
        description: "Please enter a prompt for image generation",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    const formData = new FormData();
    // Always use "artistic" for text-to-image generation
    formData.append("prompt", textPrompt);
    formData.append("feature", "artistic");

    try {
      const response = await fetch("http://localhost:8005/generate", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Text-to-image generation failed");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setGeneratedImage(url);
      toast({
        title: "Success",
        description: "Image generated successfully!",
      });
    } catch (error) {
      console.error(error);
      toast({
        title: "Error",
        description: "Failed to generate image",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto max-w-4xl py-10">
      <h1 className="text-4xl font-bold text-center mb-8">Redesign Your Room</h1>
      
      {/* Section for image transformation (requiring file upload) */}
      <div className="flex flex-col items-center gap-6">
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />
        <Button onClick={() => fileInputRef.current?.click()} className="mb-4">
          {selectedFileName ? "Change File" : "Choose File"}
        </Button>
        {selectedFileName && (
          <p className="text-sm text-gray-600">Selected File: {selectedFileName}</p>
        )}
        <div className="flex flex-wrap gap-4 justify-center">
          {transformationFeatures.map((feat) => (
            <Button
              key={feat.value}
              onClick={() => handleFeatureSelect(feat.value)}
              variant={selectedFeature === feat.value ? "default" : "outline"}
              className="capitalize"
            >
              {feat.label}
            </Button>
          ))}
        </div>
        {selectedFeature && (
          <input
            type="text"
            placeholder="Enter additional details (optional)"
            value={extraPrompt}
            onChange={(e) => setExtraPrompt(e.target.value)}
            className="border rounded p-2 w-full max-w-md"
          />
        )}
        <Button onClick={handleApply} disabled={loading} className="mt-4">
          {loading ? "Processing..." : "Apply Transformation"}
        </Button>
      </div>

      <hr className="my-10" />

      {/* New section for text-to-image generation without feature options */}
      <div className="flex flex-col items-center gap-6">
        <h2 className="text-2xl font-bold">Text to Image Generation</h2>
        <input
          type="text"
          placeholder="Enter prompt for image generation"
          value={textPrompt}
          onChange={(e) => setTextPrompt(e.target.value)}
          className="border rounded p-2 w-full max-w-md"
        />
        <Button onClick={handleTextGenerate} disabled={loading} className="mt-4">
          {loading ? "Processing..." : "Generate Image"}
        </Button>
      </div>

      {generatedImage && (
        <div className="mt-8 flex flex-col items-center">
          <img
            src={generatedImage}
            alt="Generated Transformation"
            className="max-w-md rounded shadow-lg"
          />
          <a
            href={generatedImage}
            download={`generated_artistic.jpeg`}
            className="mt-4 inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
          >
            Download Image
          </a>
        </div>
      )}
    </div>
  );
}