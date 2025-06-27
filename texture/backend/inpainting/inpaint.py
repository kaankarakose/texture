import PIL
import requests
import torch
from io import BytesIO
from diffusers import StableDiffusionInpaintPipeline, AutoPipelineForInpainting
import base64
import numpy as np
import time
import argparse

class Inpainter:
    def __init__(self, model_path="runwayml/stable-diffusion-inpainting", device="cuda"):
        """
        Initialize the Inpainter class with a specific model.
        
        Args:
            model_path (str): Path to the model or model identifier from huggingface.co/models
            device (str): Device to use for inference (cuda, cpu)
        """
        self.device = device
        self.pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16
        )
        self.blur_pipeline = AutoPipelineForInpainting.from_pretrained("runwayml/stable-diffusion-v1-5", 
            torch_dtype=torch.float16).to('cuda')
        
        self.pipeline = self.pipeline.to(device)
    
    def generate(self, prompt, init_image, mask_image, guidance_scale=5, num_inference_steps=150):
        """
        Generate inpainted image based on prompt, initial image and mask.
        
        Args:
            prompt (str): Text prompt to guide the image generation
            init_image (PIL.Image.Image): Initial image to inpaint
            mask_image (PIL.Image.Image): Mask image where white pixels are the area to inpaint
            guidance_scale (float): Scale for classifier-free guidance
            num_inference_steps (int): Number of denoising steps
            
        Returns:
            PIL.Image.Image: Generated inpainted image
        """

        init_image = self.convert_base64_to_image(init_image)
        mask_image = self.convert_base64_to_image(mask_image)

        if not isinstance(init_image, PIL.Image.Image):
            raise TypeError("init_image must be a PIL Image")
        
        if not isinstance(mask_image, PIL.Image.Image):
            raise TypeError("mask_image must be a PIL Image")

        print(f"Guidance scale: {guidance_scale}")
        print(f"Num inference steps: {num_inference_steps}")

        negative_prompt = "deformed, grotesque, surreal, abstract"


        with torch.no_grad():
            blurred_mask = self.blur_pipeline.mask_processor.blur(mask_image, blur_factor=33)

            
        with torch.no_grad():
            start = time.time()
            output = self.pipeline(
                prompt=prompt,
                image=init_image,
                negative_prompt = negative_prompt,
                mask_image=blurred_mask,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps
            )
            end = time.time()
            print(f"Time elapsed: {end - start} seconds")
        
        output = self.convert_image_to_base64(output.images[0])
        return output

    def convert_base64_to_image(self, base64_string):
        """
        Convert a base64 string to a PIL Image.
        
        Args:
            base64_string (str): Base64 encoded image string (may include data URI prefix)
            
        Returns:
            PIL.Image.Image: Decoded image
        """
        # Remove data URI prefix if present
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        # Decode base64 string
        image_data = BytesIO(base64.b64decode(base64_string))
        
        # Open image
        image = PIL.Image.open(image_data)
        image = image.convert("RGB")
        
        return image
        
    def convert_image_to_base64(self, image, format="PNG"):
        """
        Convert a PIL Image to a base64 string.
        
        Args:
            image (PIL.Image.Image): PIL Image to convert
            format (str): Image format (JPEG, PNG, etc.)
            
        Returns:
            str: Base64 encoded image string with data URI prefix
        """
        buffered = BytesIO()
        image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/{format.lower()};base64,{img_str}"


# if __name__ == "__main__":

    # parser = argparse.ArgumentParser(description='Inpaint an image')
    # parser.add_argument('--init_image', type=str, required=True, help='Path to the initial image')
    # parser.add_argument('--mask_image', type=str, required=True, help='Path to the mask image')
    # parser.add_argument('--prompt', type=str, required=True, help='Text prompt for inpainting')
    # parser.add_argument('--output', type=str, default='output.png', help='Output file path')
    
    # args = parser.parse_args()
    
    # # Load images and convert to base64
    # def read_image_to_base64(path, format="PNG"):
    #     """
    #     Read an image from a file path and convert to base64 string.
        
    #     Args:
    #         path (str): Path to the image file
    #         format (str): Image format (JPEG, PNG, etc.)
            
    #     Returns:
    #         str: Base64 encoded image string with data URI prefix
    #     """
    #     image = PIL.Image.open(path).convert("RGB")
        
    #     return image

    # # Convert input images to base64
    # init_image_base64 = read_image_to_base64(args.init_image)
    # mask_image_base64 = read_image_to_base64(args.mask_image)

    # print(args.prompt)
    
    # # Create inpainter
    # inpainter = Inpainter()
    
    # # Generate inpainted image
    # result_base64 = inpainter.generate(
    #     prompt=args.prompt,
    #     init_image=init_image_base64,
    #     mask_image=mask_image_base64,
    # )
    
    # # Convert result back to image and save
    # result_image = inpainter.convert_base64_to_image(result_base64)
    # result_image.save(args.output)
    
    # print(f"Inpainted image saved to {args.output}")