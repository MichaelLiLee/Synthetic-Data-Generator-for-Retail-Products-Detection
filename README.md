<p align="center">
<img src="docs/images/retail_top.png">
</p>

# 應用合成資料訓練物件偵測模型進行零售商品辨識 

訓練卷積神經網絡模型需要大量標記的訓練資料才能獲得良好的性能，而訓練資料的收集和標記是一個昂貴、耗時且容易出錯的過程。克服這一限制的一種有前途的方法是使用電腦合成影像(Computer Generated Imagery, CGI)技術建立一個虛擬環境來生成合成資料與進行自動標記。

## **1. 專案概述** 

Synthetic Data Generator for Retail Products Detection是一個開源專案，旨在以Blender與Python建構一個合成影像資料生成管道，生成的合成資料被用來訓練YOLOv5模型並應用於零售商品辨識用途。此專案利用Blender生成了包含63種零售商品(例如: 麥片盒、可樂鋁罐等)的隨機化合成圖像，並導出對應的資料標籤與標註(2D偵測框，YOLO格式)。

本專案包含了以下資源:
* 數位資產 - 63種零售商品的3D模型(.blend)，可由此[Google Drive]()下載。
* 數位資產 - 1369種PBR材質(.jpg)，這些材質來自ambientCG網站，可由此Google Drive下載。
* 數位資產 - 561種HDRI照明貼圖(.exr)，這些照明貼圖來自PolyHaven網站，可由此Google Drive下載。
* 數位資產 - 充當背景與干擾物的無材質幾何3D模型(.blend)，可由此Google Drive下載。
* 程式碼 - 合成影像資料生成器(SDG)，一個以Blender與Python建構的合成影像資料生成管道。
* 真實零售商品影像資料集 - 1267張真實零售商品影像資料集，此資料集來自UnityGroceries-Real Dataset，其資料標籤為YOLO格式，可由此[Google Drive](https://drive.google.com/file/d/1RPFCBf4z7A4NkskV6Jn1MYwirZqf_qtR/view?usp=sharing)下載。


## **2. 合成資料生成管道介紹**
本專案產生合成資料的流程，如圖所示，首先於虛擬場景中生成一面由隨機幾何物體與紋理的背景，接著隨機添加零售商品與干擾/遮蔽物物體至虛擬場景內，並隨機分配物體的姿態與位置，接著向虛擬場景添加隨機照明，並隨機挑選照明的強度、角度，接著隨機產生運動模糊、調整對比度、飽和度等視覺效果，最後渲染影像並產生自動物件標記。
![](docs/images/SDG_flow.png)
*圖 合成資料生成管道的流程*

#### 背景物體生成
虛擬場景的背景產生方式，是從一組包含數種簡單幾何形狀(例如:立方體、圓柱體)的 3D 模型中隨機選取，並填充至虛擬場景的背景，形成一面背景牆。3D 模型的放置位置與彼此間的距離，由給定平面範圍的泊松分布採樣產生，接著隨機旋轉背景物體的姿態。接著設定這些放置於虛擬場景中充當背景物體的表面紋理，表面紋理來自於 1369 種 PBR 紋理材質，隨機選取這些紋理材質中的一個子集並添加至背景物體的表面。

#### 前景物體生成
虛擬場景的前景產生方式，是從 63 個零售商品的 3D 資產中隨機選取一個子集，並將這些 3D 資產隨機放置於背景物體上方的區域，前景物體的放置位置與彼此間的距離，由給定空間範圍的泊松分布採樣產生。

#### 干擾/遮擋物生成
虛擬場景的干擾/遮擋物產生方式，是從一組包含數種簡單幾何形狀(例如:立方體、圓柱體)的 3D 模型中隨機選取，並將這些干擾/遮擋物隨機放置於前景物體上方的區域，遮擋物的放置位置與彼此間的距離，由給定空間範圍的泊松分布採樣產生。接著設定這些放置於虛擬場景中充當背景物體的表面紋理，表面紋理來自於 1369 種 PBR紋理材質，隨機選取這些紋理材質中的一個子集並添加至背景物體的表面。

#### 燈光照明生成
虛擬場景的燈光照明產生方式，是隨機從 581 個室內與室外 HDRI 選取一個做為場景照明，並隨機旋轉燈光的角度。

#### 圖像渲染
本研究使用 Cycles 渲染器渲染虛擬相機於虛擬場景所拍攝的影像，Cycles 是Blender 軟體的一個路徑追蹤渲染器，可以產生非常逼真的圖像效果。

#### 相機效果
為了增加合成資料的多樣性，以及模擬真實的相機效果，本研究參考了 Carlson 等人[44]所設計的相機模型，此相機效果程序如圖 37 所示，會使用多種相機效果擴增方法，以模擬影像形成和後處理過程中每個階段可能發生的視覺效果。此程序會隨機對渲染影像產生色相差、模糊、運動模糊、曝光、雜訊，以及隨機調整渲染影像的白平衡、色相、對比度、飽和度。此程序使用 Blender 中的合成(Compositing)編輯器所實現。

#### 產生檢測框標記
在完成合成資料的渲染與相機效果程序後，需要將虛擬場景中前景物體的 2D 檢測框與人體關鍵點標記出來。圖 38 顯示了檢測框產生的流程，本研究使用 blender 內建的 IDMask 功能[45]，產生個別前景物體的影像遮罩(image mask)，並使用影像遮罩計算 2D 檢測框在影像中的座標，最後輸出符合 YOLO 物件偵測器模型訓練所需的標記檔案，其格式為.txt；圖 39 顯示了關鍵點產生的流程，首先索引對應骨頭之世界座標，接著將世界座標轉換至影像座標，最後使用程式輸出符合 KeypointRCNN 模型訓練所需的標記檔案，其格式為.json。


![](docs/images/camera_effect.png) 
*相機效果生成的流程*

![](docs/images/retail_render_scene.png)
*於Blender中的虛擬場景*

<p align="center">
<img  src="docs/images/retail_generate_flow.gif">
</p>

*於Blender中生成的虛擬場景*

<p align="center">
<img  src="docs/images/retail_synth_examples.png">
</p>

*零售商品辨識合成資料影像及標記範例*

## **3. 數位資產配置與生成管道參數設定** 

<p align="center">
<img  src="docs/images/retail_model_63.png">
</p>

*63種零售商品之3D模型*

<p align="center">
<img  src="docs/images/HDRI.png" width="600"> <img  src="docs/images/ambientCG.png" width="900">
</p>
作為環境照明的hdri照明貼圖與作為背景與干擾物的pbr材質*

```python
class SDGParameter:
    """A configuration class to configure this blender-based synthetic data generator pipeline.

    Attributes
    ----------
    gen_num (int): The quantity of synthetic images needed to be generated.
    blender_exe_path (str): The path to the blender executable[1].
    asset_background_object_folder_path (str): The path to background object assets.
    asset_foreground_object_folder_path (str): The path to foreground object assets.
    asset_ambientCGMaterial_folder_path (str): The path to the downloaded ambientCG PBR materials.
    asset_hdri_lighting_folder_path (str): The path to the downloaded Poly Haven HDRIs.
    asset_occluder_folder_path (str): The path to occlusion object assets.
    output_img_path (str): The path where rendered images will be saved.
    output_label_path (str): The path where YOLO format bounding box annotations will be saved.
    background_poisson_disk_sampling_radius (float): Background objects separation distance.
    num_foreground_object_in_scene_range (dict of str: int): The distribution of the number of retail items within the blender scene.
    foreground_area (list of float): Spatial distribution area of foreground objects.
    foreground_poisson_disk_sampling_radius (float): Foreground objects separation distance.
    num_occluder_in_scene_range (dict of str: int): The distribution of the number of occlusion objects within the blender scene.
    occluder_area (list of float): Spatial distribution area of occlusion objects.
    occluder_poisson_disk_sampling_radius (float): Occlusion objects separation distance.
    bg_obj_scale_ratio_range (dict of str: float): The distribution of the scale ratio of background objects within the blender scene.
    fg_obj_scale_ratio_range (dict of str: float): The distribution of the scale ratio of foreground objects within the blender scene.
    occluder_scale_ratio_range (dict of str: float): The distribution of the scale ratio of occluder objects within the blender scene.
    hdri_lighting_strength_range (dict of str: float): The distribution of the strength factor for the intensity of the HDRI scene light.
    img_resolution_x (int): Number of horizontal pixels in the rendered image.
    img_resolution_y (int): Number of vertical pixels in the rendered image.
    max_samples (int): Number of samples to render for each pixel.
    chromatic_aberration_probability (float): Probability of chromatic aberration effect being enabled.
    blur_probability (float): Probability of blur effect being enabled.
    motion_blur_probability (float): Probability of motion blur effect being enabled.
    exposure_probability (float): Probability of exposure adjustment being enabled.
    noise_probability (float): Probability of noise effect being enabled.
    white_balance_probability (float): Probability of white balance adjustment being enabled.
    brightness_probability (float): Probability of brightness adjustment being enabled.
    contrast_probability (float): Probability of contrast adjustment being enabled.
    hue_probability (float): Probability of hue adjustment being enabled.
    saturation_probability (float): Probability of saturation adjustment being enabled.
    chromatic_aberration_value_range (dict of str: float): The distribution of the value of Lens Distortion nodes input-Dispersion, which simulates chromatic aberration.
    blur_value_range (dict of str: int): The distribution of the value of Blur nodes input-Size, which controls the blur radius values.
    motion_blur_value_range (dict of str: int): The distribution of the value of Vector Blur nodes input-Speed, which controls the direction of motion.
    exposure_value_range (dict of str: float): The distribution of the value of Exposure nodes input-Exposure, which controls the scalar factor to adjust the exposure.
    noise_value_range (dict of str: float): The distribution of the value of brightness of the noise texture.
    white_balance_value_range (dict of str: int): The distribution of the value of WhiteBalanceNode input-ColorTemperature, which adjust the color temperature.
    brightness_value_range (dict of str: float): The distribution of the value of Bright/Contrast nodes input-Bright, which adjust the brightness.
    contrast_value_range (dict of str: float): The distribution of the value of Bright/Contrast nodes input-Contrast, which adjust the contrast.
    hue_value_range (dict of str: float): The distribution of the value of Hue Saturation Value nodes input-Hue, which adjust the hue.
    saturation_value_range (dict of str: float): The distribution of the value of Hue Saturation Value nodes input-Saturation, which adjust the saturation.

    """
        def __init__(self):
        self.gen_num = 2
        self.blender_exe_path = "C:/program Files/Blender Foundation/Blender 3.3/blender"
        self.asset_background_object_folder_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/Assets/background_object"
        self.asset_foreground_object_folder_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/Assets/foreground_object"
        self.asset_ambientCGMaterial_folder_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/Assets/texture"
        self.asset_hdri_lighting_folder_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/Assets/HDRI"
        self.asset_occluder_folder_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/Assets/occluder"
        self.output_img_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/gen_data/images"
        self.output_label_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/gen_data/labels"
        self.background_poisson_disk_sampling_radius = 0.2
        self.num_foreground_object_in_scene_range = {"min": 8 ,"max": 20}
        self.foreground_area = [2.5, 1.5, 0.5]
        self.foreground_poisson_disk_sampling_radius = 0.3
        self.num_occluder_in_scene_range = {"min": 5 , "max": 10} # !!maximum : 20
        self.occluder_area = [1.2, 0.8, 0.4]
        self.occluder_poisson_disk_sampling_radius = 0.25
        self.bg_obj_scale_ratio_range = {"min": 2.5, "max": 2.5}
        self.fg_obj_scale_ratio_range = {"min": 0.5, "max": 2.5}
        self.occluder_scale_ratio_range = {"min": 0.5, "max": 1.5}
        self.hdri_lighting_strength_range = {"min": 0.2 , "max": 2.2}
        self.img_resolution_x = 1728
        self.img_resolution_y = 1152
        self.max_samples = 256
        self.chromatic_aberration_probability = 0.1
        self.blur_probability = 0.1
        self.motion_blur_probability = 0.1
        self.exposure_probability = 0.15
        self.noise_probability = 0.1
        self.white_balance_probability = 0.15
        self.brightness_probability = 0.15
        self.contrast_probability = 0.15
        self.hue_probability = 0.15
        self.saturation_probability = 0.15
        self.chromatic_aberration_value_range = {"min": 0.1, "max": 1}
        self.blur_value_range = {"min": 2, "max": 4}
        self.motion_blur_value_range = {"min": 2, "max": 7}
        self.exposure_value_range = {"min": -0.5, "max": 2}
        self.noise_value_range = {"min": 1.6, "max": 1.8}
        self.white_balance_value_range = {"min": 3500, "max": 9500}
        self.brightness_value_range = {"min": -1.0, "max": 1.0}
        self.contrast_value_range = {"min": -1.0, "max": 5.0}
        self.hue_value_range =  {"min": 0.45, "max": 0.55}
        self.saturation_value_range = {"min": 0.75, "max": 1.25}

```
## **4. YOLOv5模型訓練及結果** 

