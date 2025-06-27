import json
import requests
import base64
import logging
from dataclasses import dataclass
from websockets.sync.client import connect
from typing import Dict, Any, Optional
import time
import os

logger = logging.getLogger(__name__)

@dataclass
class Parameters:
    positive_prompt: str
    negative_prompt: str
    reference_img: str
    
@dataclass
class ParametersMapping:
    positive_prompt: str
    negative_prompt: str
    reference_img: str
    
MAPPING = ParametersMapping(
    positive_prompt="7",
    negative_prompt="9",
    reference_img="10",
)

class ComfyUIAPI:
    def __init__(self):
        self.workflow_path = "/mnt-persist/Kaan/texture-app/backend/src/ai_proxy/services/resources/character.json"

    def upload_img(self, img_path):
        url = "http://localhost:8189/upload/image"
        response = requests.post(url, files={"image": (os.path.basename(img_path), open(img_path, "rb"))})
        print(response)


    def get_workflow(self, parameters: Parameters):
        with open(self.workflow_path, "r") as f:
            workflow = json.load(f)
            
        workflow[MAPPING.positive_prompt]["inputs"]["text"] = parameters.positive_prompt
        workflow[MAPPING.negative_prompt]["inputs"]["text"] = parameters.negative_prompt
        workflow[MAPPING.reference_img]["inputs"]["image"] = parameters.reference_img
        ## TODO:     
        return workflow

    def generate_img(self, workflow, img_prefix="no_bg"):
       
        url = "http://localhost:8189/prompt"
        response = requests.post(url, json={"prompt": workflow, "api":True})
        data = response.json()
        print(data)
        prompt_id = data["prompt_id"]
       
        print("ID ", prompt_id)
        
        time.sleep(2)
        
        with connect("ws://localhost:8189/ws") as websocket:
            while True:
                message = websocket.recv()
                data = json.loads(message)
                print(data)
                if data["type"] == "executing":
                    print(f"Progress: {data['data']['node']}")
                elif data["type"] == "status" and data["data"]["status"]["exec_info"]["queue_remaining"] == 0:
                    print("Execution complete")
                    break
                
        history_url = f"http://localhost:8189/history/{prompt_id}"
        history_response = requests.get(history_url)
        history_data = history_response.json()
        
        #print(history_data)

        img_name = "character.jpg"
        for node_id, node_output in history_data[prompt_id]["outputs"].items():
            if "images" in node_output:
                for image in node_output["images"]:
                    print(image["filename"])
                    if img_prefix in image["filename"]:
                        image_url = f"http://localhost:8189/view?filename={image['filename']}"
                        print(image_url)
                        img_data = requests.get(image_url).content
                        #with open(img_name, 'wb') as handler:
                            #handler.write(img_data)
                            
                        return img_data
    


initial_pose = "/mnt-persist/Kaan/texture-app/backend/src/ai_proxy/services/resources/poses/pose1.jpg"




defined_poses = {
    "pose2.jpg": "thinking",
    "pose7.jpg": "wrong",
    "pose8.jpg": "yay"

}

class ComfyUIAPIWrapper:
    """Wrapper for ComfyUIAPI to handle POST requests"""
    
    def __init__(self, base_url: str = None):
        self.comfy_api = ComfyUIAPI()
        self.base_url = base_url or "http://localhost:8189"
        self.poses_dir = os.path.join(os.path.dirname(__file__), 'resources', 'poses')
    
    
    def _save_base64_to_file(self, base64_string: str, filename: str) -> str:
        """Save a base64 encoded string to a file
        
        Args:
            base64_string: The base64 encoded string
            filename: The name of the file to save
            
        Returns:
            The path to the saved file
        """
        try:
            # Remove the data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode the base64 string
            image_data = base64.b64decode(base64_string)
            
            # Save to file
            file_path = os.path.join(os.path.dirname(__file__), 'temp', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(image_data)
                
            return file_path
        except Exception as e:
            logger.error(f"Error saving base64 to file: {str(e)}")
            raise
    
    def _cleanup_temp_files(self, file_paths: list) -> None:
        """Clean up temporary files
        
        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {str(e)}")
                
    def generate_avatar_with_poses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an initial avatar pose and then create additional poses
        
        Args:
            params: Dictionary containing the following keys:
                - image: Base64 encoded image (optional)
                - positive_prompt: Positive prompt for image generation
                - negative_prompt: Negative prompt for image generation
                
        Returns:
            Dictionary containing all generated poses as Base64 strings:
                - initial_pose: Base64 encoded initial pose
                - pose1: Base64 encoded pose 1
                - pose2: Base64 encoded pose 2
                - etc.
        """
     
        positive_prompt = params.get('positive_prompt', '')

        positive_prompt = f"{positive_prompt},(looking at camera:1.3),(atmosphere), coherent, continuity, epic, plain background"""
        negative_prompt = """
                        logo, logos, images, graphics, text,
                        embedding:verybadimagenegative_v1.3, (3d), white eyes, layout, (worst quality:1.4),(low quality:1.4),(normal quality:1.3),
                        lowres,watermark, title, (jpeg-artifacts:1.33), embedding:badhandv4, embedding:bad-artist, embedding:bad-artist-anime, (hands:1.5)
                        """
        
        # Validate parameters
        if not positive_prompt:
            return {"error": "Missing positive_prompt parameter"}
        
        # Dictionary to store all poses
        poses_dict = {}
        
        # Generate initial pose
        logger.info("Generating initial pose...")
        
        
            
        # Create parameters for the workflow
        comfy_params = Parameters(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            reference_img=os.path.basename(initial_pose)
        )
        
        # Get the workflow and generate the initial pose
        workflow = self.comfy_api.get_workflow(comfy_params)
        self.comfy_api.upload_img(initial_pose)

        initial_pose_data = self.comfy_api.generate_img(workflow)
        
        # Convert the initial pose to base64 and add to dictionary
        
        initial_pose_base64 = base64.b64encode(initial_pose_data).decode('utf-8')
        poses_dict["initial_pose"] = initial_pose_base64
        
        # Now generate additional poses using the pose files
        logger.info("Generating additional poses...")
        pose_files = sorted([f for f in os.listdir(self.poses_dir) if f.endswith('.jpg')])
        
        for pose_file in pose_files:

            pose_name = os.path.basename(pose_file)  # Get name without extension
            if pose_name not in defined_poses:
                continue
            logger.info(f"Generating {pose_name}...")
            
            # Upload the pose file to ComfyUI
            pose_path = os.path.join(self.poses_dir, pose_file)
            self.comfy_api.upload_img(pose_path)
            
            # Create parameters for the workflow with the pose file
            pose_params = Parameters(
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                reference_img=pose_name
            )
            
            # Get the workflow and generate the pose
            pose_workflow = self.comfy_api.get_workflow(pose_params)
            pose_image_data = self.comfy_api.generate_img(pose_workflow)
            
            # Convert the pose to base64 and add to dictionary
            
            pose_base64 = base64.b64encode(pose_image_data).decode('utf-8')
            poses_dict[defined_poses[pose_name]] = pose_base64
                
          
        
        return poses_dict
            


if __name__ == "__main__":
   


   cAPIWrapper = ComfyUIAPIWrapper()

   cAPIWrapper.generate_avatar_with_poses({
       'positive_prompt': 'attractive 20yo 1girl, anime, cartoon, pink eyes, black hair, shoulder length hair, plain white t-shirt, blue mini skirt'
   })









































