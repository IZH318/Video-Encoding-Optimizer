# Video Encoding Optimizer

<p align="center">
  <img src="https://img.shields.io/badge/Windows-8.1%2B-0078D6.svg?style=flat-square&logo=windows&logoColor=white" alt="OS: Windows 8.1+">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square" alt="License: GPL v3">
  <img src="https://img.shields.io/badge/Powered%20by-FFmpeg-4E963A.svg?style=flat-square&logo=ffmpeg&logoColor=white" alt="Powered by FFmpeg">
</p> <br>

<img width="802" height="652" alt="캡처_2025_09_04_05_56_43_601" src="https://github.com/user-attachments/assets/b90500b7-27c6-4dc4-ad5b-eea3a382a6a4" /> <br>

**A GUI Application for Finding Optimal Video Encoding Settings** <br>
This application helps you find the perfect balance between quality (VMAF), file size, and encoding speed by testing various codecs and settings. <br>
It empowers you to make data-driven, rational decisions without having to deal with complex FFmpeg commands directly. <br>

<br>

## 🖼️ Preview

### 1. Main UI
<img width="802" height="652" alt="캡처_2025_09_04_04_13_09_118" src="https://github.com/user-attachments/assets/b31a63b0-65a1-44c0-9bf4-7a0f4e258eb7" />

> Control all core functions—such as codec selection, optimization mode, and sampling method—and view real-time analysis results from a single-window interface.

<br>

### 2. Interactive Graph
<img width="902" height="732" alt="캡처_2025_09_04_04_22_13_133" src="https://github.com/user-attachments/assets/07077e21-938b-431e-9c0f-338e4e57f82b" />

> Visualize all encoding results as a 2D scatter plot to intuitively analyze the correlation between data points.
> 
> Freely change the X/Y axes and zoom/pan to explore the data in depth.

<br>

### 3. A/B Comparison
**▼ Original Sample** <br>
<img width="1920" height="1080" alt="original_sample mkv_snapshot_00 07 006" src="https://github.com/user-attachments/assets/1b573ffa-d91f-4d82-b7ed-0f943e3f4509" />

> A scene from the original video, which serves as the baseline for comparison.
<details>
<summary>📄 View MediaInfo for the original video file</summary>

```text
General
ID                             : 0 (0x0)
Complete name                  : C:\Users\Administrator\Desktop\Video Encoding Optimizer\【BDMux】 TV 明日ちゃんのセーラー服 EP11.m2ts
Format                         : BDAV
Format/Info                    : Blu-ray Video
File size                      : 7.04 GiB
Duration                       : 23 min 41 s
Overall bit rate mode          : Variable
Overall bit rate               : 42.6 Mb/s
Maximum Overall bit rate       : 48.0 Mb/s
Frame rate                     : 23.976 FPS

Video
ID                             : 4113 (0x1011)
Menu ID                        : 1 (0x1)
Format                         : AVC
Format/Info                    : Advanced Video Codec
Format profile                 : High@L4.1
Format settings                : CABAC / 4 Ref Frames
Format settings, CABAC         : Yes
Format settings, Reference fra : 4 frames
Format settings, Slice count   : 4 slices per frame
Codec ID                       : 27
Duration                       : 23 min 41 s
Bit rate mode                  : Variable
Bit rate                       : 36.2 Mb/s
Maximum bit rate               : 40.0 Mb/s
Width                          : 1 920 pixels
Height                         : 1 080 pixels
Display aspect ratio           : 16:9
Frame rate                     : 23.976 (24000/1001) FPS
Color space                    : YUV
Chroma subsampling             : 4:2:0
Bit depth                      : 8 bits
Scan type                      : Progressive
Bits/(Pixel*Frame)             : 0.729
Time code of first frame       : 01:00:00:00
Stream size                    : 6.00 GiB (85%)

Audio #1
ID                             : 4352 (0x1100)
Menu ID                        : 1 (0x1)
Format                         : PCM
Format settings                : Big / Signed
Muxing mode                    : Blu-ray
Codec ID                       : 128
Duration                       : 23 min 41 s
Bit rate mode                  : Constant
Bit rate                       : 2 304 kb/s
Channel(s)                     : 2 channels
Channel layout                 : L R
Sampling rate                  : 48.0 kHz
Bit depth                      : 24 bits
Stream size                    : 390 MiB (5%)

Audio #2
ID                             : 4353 (0x1101)
Menu ID                        : 1 (0x1)
Format                         : PCM
Format settings                : Big / Signed
Muxing mode                    : Blu-ray
Codec ID                       : 128
Duration                       : 23 min 41 s
Bit rate mode                  : Constant
Bit rate                       : 2 304 kb/s
Channel(s)                     : 2 channels
Channel layout                 : L R
Sampling rate                  : 48.0 kHz
Bit depth                      : 24 bits
Stream size                    : 390 MiB (5%)
```
</details>

<br>

Now, let's compare two different encoding settings. Both tests were conducted under the following common conditions:
- **Encoder Group**: `Software`
- **Codec**: `libx264`
- **Sample Selection**: `Auto (Complex Scene)`
- **Durations (s)**: `7`
- **Analysis Method**: `Single-Point`

<br>

**▼ Difference A - *Preset: fast, CRF: 21*** <br>
<img width="1920" height="1080" alt="diff_A_fast_21_vs_Original mkv_snapshot_00 07 006" src="https://github.com/user-attachments/assets/eced6aad-9eed-4c18-a0f1-e46a7d9266c7" />

<br>

**▼ Difference B - *Preset: ultrafast, CRF: 51*** <br>
<img width="1920" height="1080" alt="diff_B_ultrafast_51_vs_Original mkv_snapshot_00 07 006" src="https://github.com/user-attachments/assets/cb0f4126-0c7f-437f-9635-0165a40a43a9" />

> The two images above visualize how different **Setting A** and **Setting B** are from the original video.
>
> In **Difference A**, only some outlines are faintly visible, whereas **Difference B** shows much brighter and more distinct outlines.
> 
> This indicates that more information was lost with Setting B, meaning **Setting A is the superior result that better preserves the original quality**.

<br>

### 4. HTML Report
![screencapture-file-C-Users-Administrator-Desktop-Video-Encoding-Optimizer-Resource-ep11test-html-2025-09-04-04_48_58 (Resize)](https://github.com/user-attachments/assets/5a63eadf-7cf2-4301-872a-5daaaab5bda9)

> Export all analysis results, test parameters, recommended settings, and an interactive Chart.js-based graph into a single HTML file.
> 
> This report is very useful for archiving analysis or sharing it with others.

<br>

## 🌟 Key Features

-   **Wide Codec Support**:
    -   **Software**: `libx264`, `libx265`, `libaom-av1`, `svt-av1`, `librav1e`, etc.
    -   **Hardware Acceleration**: Full support for H.264/HEVC/AV1 encoding via NVIDIA (NVENC), Intel (QSV), and AMD (AMF).
-   **Automated Sample Extraction & Analysis**:
    -   **Intelligent Scene Detection**: Automatically finds the most complex or simple scenes in the video and extracts them as test samples. Users can choose between parallel or sequential analysis to speed up the process.
    -   **Accurate Quality Measurement**: Precisely analyzes various quality metrics, with VMAF as the primary metric, alongside PSNR, SSIM, and Block Score.
-   **Powerful Parallel Processing**:
    -   Leverages multiprocessing to run multiple encoding jobs simultaneously, drastically reducing analysis time (based on the number of physical CPU cores).
-   **Two Advanced Optimization Modes**:
    -   **Range Test**: Tests all combinations within a specified range of presets and quality levels (CRF/CQ/QP) to map out the overall performance distribution.
    -   **Target VMAF**: Intelligently searches for the most efficient setting (the highest CRF value) for each preset that meets a target VMAF score. These searches run in parallel to maximize speed.
-   **In-depth Result Analysis & Visualization**:
    -   **Interactive Graph**: Visualizes all test results in a `Chart.js`-based 2D scatter plot, allowing you to analyze data from different perspectives by freely changing the X/Y axes.
    -   **Pareto Front**: Automatically highlights the most efficient encoding options that are superior to all other settings in every aspect.
    -   **Sweet Spot**: Automatically recommends the "best bang for the buck" point from the Pareto Front results, representing the most balanced trade-off between quality and file size.
-   **Robust Format Handling**:
    -   **Advanced Support for Broadcast Formats (M2TS, TS)**: Automatically corrects timestamp offsets (PTS offset) common in broadcast streams and detects interlaced video, deinterlacing it automatically for accurate analysis.
    -   **Color Information Preservation**: Detects the original video's color metadata (Color Space, Range, Primaries, etc.) and explicitly applies it during encoding to prevent color distortion in HDR/SDR videos.
    -   **Dynamic File Support**: Automatically recognizes and displays nearly all video formats supported by FFmpeg in the file selection dialog.
-   **User Convenience Features**:
    -   **Automatic FFmpeg Download & Setup**: If FFmpeg is not found at startup, the application automatically downloads and sets up the latest version.
    -   **VMAF Model Management**: Download official VMAF models from Netflix with a single click and apply them to your tests.
    -   **A/B Comparison Sample Generation**: Select two results to instantly generate sample videos for side-by-side comparison with the original, as well as a "difference" video.
    -   **Final Command Generation**: Automatically generates the FFmpeg command for your chosen optimal setting, ready to be copied to the clipboard to apply to the full video.
    -   **Detailed Report Export**: Save all analysis results as CSV data or as a single, comprehensive HTML report that includes an interactive graph.

<br>

## ⚙️ How it Works

This tool follows a systematic process to find the optimal encoding settings.

1.  **Step 1: Intelligent Sample Extraction**
    -   When a user selects 'Auto' mode, the tool performs a quick scan of the entire video using FFprobe. During this scan, it analyzes the **data size of each frame (`pkt_size`)** to measure scene complexity. The user can choose between **Parallel Analysis** and **Sequential Analysis**.
    -   **Complex Scene**: Finds the segment with the **highest sum of data size per second**. This section, rich in motion and detail, demands the highest bitrate and is ideal for testing a codec's ability to preserve detail and its performance limits.
    -   **Simple Scene**: Finds the segment with the **lowest sum of data size per second**. This section, typically static and flat, is prone to blocking artifacts at low bitrates and is well-suited for evaluating a codec's compression efficiency.
    -   **Analysis Method**: Two algorithms are available for finding the optimal segment.
        -   **Sliding Window**: Moves a 'window' of the specified sample `Duration` across the entire per-second data size map, calculating the **average complexity** for each window. This method is more stable and extracts a more representative sample by identifying sustained periods of high (or low) complexity, rather than instantaneous peaks.
        -   **Single-Point**: Finds the single 1-second point with the highest (or lowest) complexity and creates the sample centered around that time. This is faster as it skips the sliding window calculation but risks selecting a momentary data spike that may not represent the video's overall characteristics.
    -   The identified segment is quickly extracted using a lossless codec to preserve original quality and saved as a temporary file. Special preprocessing, such as correcting timestamp offsets and detecting interlacing, is applied for broadcast formats like M2TS.

2.  **Step 2: Parallel Encoding & Analysis**
    -   A list of `EncodingTask` objects is created for all user-defined test combinations. The original video's color information is extracted beforehand and included in each task.
    -   Using Python's `multiprocessing.Pool`, multiple worker processes are created based on the number of physical CPU cores.
    -   Each worker process independently takes an `EncodingTask`, runs FFmpeg to encode the sample, and calculates quality metrics like VMAF, PSNR, and SSIM. This parallel processing allows dozens of tests in **'Range Test'** mode or multiple preset searches in **'Target VMAF'** mode to run concurrently.

3.  **Step 3: Result Aggregation & In-depth Analysis**
    -   Results from all workers (VMAF scores, file sizes, etc.) are asynchronously sent back to the main thread and update the UI in real-time.
    -   Once all tests are complete, advanced analysis is performed:
        -   **Pareto Front Calculation**: Identifies the set of optimal results that are not 'dominated' by any other result (i.e., no other result has a higher VMAF score for a smaller file size).
        -   **Sweet Spot Search**: On the calculated Pareto Front, it finds the point furthest from a hypothetical line connecting the start and end points of the graph. This point typically corresponds to the 'knee point,' representing the most balanced setting, and is recommended.

4.  **Step 4: Visualization & Final Output**
    -   All analyzed data is visualized as an interactive graph using Matplotlib and Chart.js. Users can change the X and Y axes to their desired metrics to intuitively grasp the correlations in the data.
    -   Users can select their preferred setting from the results table or graph to generate the final FFmpeg command needed to apply it to the entire video.

<br>

## 🚀 Installation & Usage

### Requirements
-   **Operating System**: Windows 8.1 or newer
-   **Python**: 3.10 or newer [[**Download**]](https://www.python.org/downloads/windows/)

<br>

### Installation
1.  Download the latest version from the [**Releases**](https://github.com/IZH318/Video-Encoding-Optimizer/releases) page.
2.  Open a terminal in the project directory and install the required libraries using one of the following two methods:

    **Method A: Direct Installation**
    ```bash
    pip install matplotlib psutil requests
    ```

    **Method B: Using `requirements.txt`**
    ```bash
    pip install -r requirements.txt
    ```
3.  Run `Video Encoding Optimizer.py`.

<br>

### Detailed User Guide

#### 1. Select Video File
-   Click the `Select Video...` button to choose the video file you want to analyze.

<br>

#### 2. Configure Encoding Settings

-   **Encoder Group & Codec**:
    -   The application automatically detects encoders installed on your system and groups them (e.g., Software, NVENC).
    -   Select a group to see a list of available codecs (e.g., `libx265`, `hevc_nvenc`). Choose your desired codec.
-   **Preset Range**:
    -   Specify the range of encoding speed/compression presets to test. For example, selecting `fast` to `veryslow` will include all presets in between (`fast`, `medium`, `slow`, `slower`, `veryslow`) in the test.
-   **Optimization Mode**:
    -   **Range Test**: Tests all quality values (CRF/CQ) from the start to the end of the specified range. For instance, a CRF range of 18-22 will test 18, 19, 20, 21, and 22.
    -   **Target VMAF**: Set a target VMAF score, and the application will intelligently find the most efficient setting (highest CRF value) for each preset that meets this score. This mode processes the search for each preset in parallel to maximize efficiency.
-   **Audio**:
    -   Choose whether to `Copy Audio` from the source or `Remove Audio`.
-   **Parallel Jobs & NVENC Warning**: You can adjust the number of 'Parallel Jobs'. When using NVENC codecs, setting this value above the hardware limit may cause errors.
    -   As per NVIDIA's official policy, most GeForce series GPUs have a driver-level limit on the number of concurrent encoding sessions.
        -   For precise information, check the [[**NVIDIA VIDEO ENCODE AND DECODE GPU SUPPORT MATRIX**]](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new).

<br>

#### 3. Select Sample

-   **Auto**:
    -   **Complex Scene**: Automatically finds and tests a scene with high detail and complexity. Ideal for evaluating a codec's detail preservation capabilities.
    -   **Simple Scene**: Finds and tests a flat scene with minimal color variation. Good for assessing blocking artifacts at low bitrates.
    -   `Duration (s)`: Set the length of the sample to be extracted, in seconds.
-   **Analysis Method**:
    -   `Sliding Window` (Default): Analyzes entire segments of the specified `Duration` to find the most representative scene. Provides more stable and reliable analysis.
    -   `Single-Point`: Finds the most complex (or simple) 'moment' (1 second) and creates the sample around that point. Faster analysis but may not be representative of the whole video.
-   **Manual**:
    -   Click the `Set Range...` button to manually specify the start and end times for the sample in HH:MM:SS.ms format.
-   **Sample Preview**: Use `ffplay` to preview the currently configured sample segment.

<br>

#### 4. Advanced Settings and Additional Options

-   **Advanced Settings...**: Opens a separate window with fine-grained controls for options specific to the selected codec (e.g., `aq-mode`, `psy-rd`, `lookahead`). Tooltip descriptions are provided for each option.
-   **Add Metrics**: Choose whether to calculate PSNR, SSIM, and Block Score in addition to VMAF. This will add a small amount of extra analysis time.
-   **VMAF Model**: After downloading official VMAF models with the `Download/Update Models` button, you can use the `Browse...` button to select a model optimized for a specific resolution or device (e.g., `vmaf_4k_v0.6.1.json`) for the analysis.

<br>

#### 5. Start Optimization
-   After configuring all settings, press the `Start Optimization` button to begin the analysis. A progress bar and status messages will show the current progress.
-   Click the `Cancel` button to immediately stop all ongoing tasks.

<br>

#### 6. Review and Utilize Results

-   **Results Table**:
    -   All test results are added to the table in real-time. You can sort the results by clicking on the column headers.
    -   **Color Highlights**:
        -   🟡 **Sweet Spot**: The recommended setting with the most ideal balance between quality and file size.
        -   🟢 **Pareto Optimal**: Efficient settings. No other setting is strictly better than these.
        -   🟣 **Lowest VMAF**: The setting that recorded the lowest VMAF score during the test.
        -   🔴 **Least Efficient**: The most inefficient setting (lowest VMAF/MB).

-   **Result Action Buttons**:
    -   **View Graph**: View the results in an interactive graph. You can zoom with the mouse wheel, pan by dragging, and hover over points to see detailed tooltips.
    -   **A/B Compare**: Select two results from the table and click this button. It will generate two sample videos encoded with those settings, along with a 'Difference' video showing the deviation from the original, and save them in a folder. This is very useful for visually comparing quality differences.
    -   **View Command**: Select a single result in the table to generate and display the `ffmpeg` command required to apply those settings to the full video.
    -   **View Log**: View the complete `ffmpeg` log generated during the encoding and analysis of a selected result, which can be helpful for troubleshooting.
    -   **Export Results**: Export all results to a CSV file or a single HTML file containing all information and the interactive graph.

<br>

## 🔧 Analysis of Core Mechanisms

-   **Architecture**:
    -   The `VideoOptimizerApp` class manages the main GUI and application logic.
    -   The `EncodingTask` data class structures all parameters required for each encoding job.
    -   The `FFmpegCommandBuilder` class dynamically generates FFmpeg commands based on an `EncodingTask`, enhancing code reusability and maintainability.
    -   The `perform_one_test` function is designed to process a single `EncodingTask` and is executed in a separate process via `multiprocessing`. This bypasses the Global Interpreter Lock (GIL) to achieve true parallelism for CPU-intensive encoding tasks.

<br>

-   **Intelligent Scene Detection**:
    -   **Frame Size Analysis**: For complex scene detection, it analyzes the **packet size (`pkt_size`)** per frame extracted via FFprobe. This data size directly correlates with scene complexity (motion, detail), allowing it to effectively find segments with the highest or lowest data volume.
    -   **Two-Pass Hybrid Parallel Analysis**: When parallel analysis is selected, the first pass quickly scans the entire video to extract only the timestamps of keyframes (I-frames). In the second pass, this list of timestamps is used to divide the analysis into chunks, which are assigned to different CPU cores for detailed, parallel frame analysis. This minimizes disk I/O contention and maximizes speed.

<br>

-   **Dynamic UI Generation & Scalability**:
    -   The `CODEC_CONFIG` dictionary acts as a central schema that manages the settings for all codecs (presets, quality ranges, advanced options, etc.).
    -   The `AdvancedSettingsWindow` reads this schema to dynamically generate appropriate UI widgets (comboboxes, spinboxes, checkboxes, etc.) for each codec, creating a highly scalable architecture where new codecs or options can be added easily.

<br>

-   **Robust Media Handling**:
    -   **Color Preservation**: The `get_color_info` function uses FFprobe to extract the original video's color metadata (Color Space, Range, Primaries, TRC) and explicitly adds it to each encoding command. This prevents distortions that can occur during color space conversion and accurately maintains the original color fidelity.
    -   **Broadcast Stream Handling**: Automatically detects PTS (Presentation Time Stamp) offsets in M2TS/TS streams and normalizes all timestamps to start from zero. It also detects interlaced video and automatically deinterlaces it with the `bwdif` filter before analysis to improve accuracy.
    -   **A/B Comparison**: Uses the `blend=all_mode=difference` filter to generate a 'Difference' video that visualizes the pixel-level differences between two videos.

<br>

-   **Core Analysis Metrics & Algorithms**:
    -   **IQR Outlier Removal**:
        - Prevents momentary data errors (e.g., corrupted frames) or extreme values from distorting the overall analysis results during scene analysis.
          - It uses the statistical **Interquartile Range (IQR)** method to identify and remove data points that fall outside the normal range.
          - Specifically, the code uses the **lower 15% and upper 85%** percentiles instead of the standard Q1 (25%) and Q3 (75%) for more stable analysis.

        **LaTeX Formula**
        ```math
        \text{IQR} = Q_{0.85} - Q_{0.15} \\
        \text{Lower Bound} = Q_{0.15} - (k \times \text{IQR}) \\
        \text{Upper Bound} = Q_{0.85} + (k \times \text{IQR})
        ```
        *(Here, k is a multiplier that adjusts the sensitivity of outlier detection; the code uses 3.0.)*

        **Plain Code Logic**
        ```
        IQR = Percentile(Data, 85) - Percentile(Data, 15)
        Lower_Bound = Percentile(Data, 15) - (3.0 * IQR)
        Upper_Bound = Percentile(Data, 85) + (3.0 * IQR)
        
        // Data is considered valid only if it is between Lower_Bound and Upper_Bound
        Valid_Data = {d | d for d in dataset if Lower_Bound <= d <= Upper_Bound}
        ```

    <br>

    -   **VMAF 1% Low**:
        - Measures 'quality consistency,' which is difficult to assess from the average VMAF score alone.
          - It's a metric designed to catch cases where the average score is high, but quality drops sharply in certain segments.
          - It calculates the average of the bottom 1% of all frame VMAF scores after sorting them.
        
        **LaTeX Formula**
        ```math
        S = \{v_1, v_2, \dots, v_n\} \quad (\text{where } v_i \le v_{i+1}) \\
        N_{1\%} = \lfloor n \times 0.01 \rfloor \\
        \text{VMAF}_{1\%\text{ Low}} = \frac{1}{N_{1\%}+1} \sum_{i=1}^{N_{1\%}+1} v_i
        ```
        **Plain Code Logic**
        ```
        All_VMAF_Scores = sorted([...])
        One_Percent_Index = floor(length(All_VMAF_Scores) * 0.01)
        
        // Scores corresponding to the bottom 1% (including at least one)
        Lowest_Scores = All_VMAF_Scores[0 ... One_Percent_Index]
        
        VMAF_1_Percent_Low = average(Lowest_Scores)
        ```

    <br>

    -   **Efficiency Metric**:
        - A key metric for quantitatively evaluating the 'cost-effectiveness' of an encoding setting, using the formula **VMAF Score / File Size (MB)**.
          - It represents how much VMAF quality is achieved per megabyte of data.

        **LaTeX Formula**
        ```math
        \text{Efficiency} = \frac{\text{VMAF}_{\text{mean}}}{\text{File Size (MB)}}
        ```
        **Plain Code Logic**
        ```
        Efficiency = VMAF_Score / File_Size_in_MB
        ```

    <br>

    -   **'Sweet Spot' Search Algorithm (Perpendicular Distance Heuristic)**:
        - Uses a geometric heuristic to find the most balanced point between quality and file size among the Pareto Front results.
          - It finds the point `P₀(size₀, vmaf₀)` that is furthest from the straight line connecting the start point `P₁(size₁, vmaf₁)` and end point `P₂(size₂, vmaf₂)` of the Pareto Front.

        **LaTeX Formula**
        ```math
        d = \frac{|(y_2 - y_1)x_0 - (x_2 - x_1)y_0 + x_2y_1 - y_2x_1|}{\sqrt{(y_2 - y_1)^2 + (x_2 - x_1)^2}}
        ```
        *In the actual code, the denominator is a constant for all points, so only the numerator is calculated to find the maximum value for performance reasons.*
        
        **Plain Code Logic**
        ```
        P_start = (size_min, vmaf_at_min)
        P_end = (size_max, vmaf_at_max)
        
        // Calculate the following value for every Pareto Front point P_current
        P_current = (current_size, current_vmaf)
        
        // Numerator part of the point-to-line distance formula
        distance_numerator = abs(
            (P_end.y - P_start.y) * P_current.x - 
            (P_end.x - P_start.x) * P_current.y + 
            P_end.x * P_start.y - P_end.y * P_start.x
        )
        
        // The P_current that maximizes 'distance_numerator' is the Sweet Spot
        SweetSpot = Point P_current that maximizes the distance_numerator
        ```

    <br>

    -   **'Target VMAF' Search Algorithm (Hybrid Search)**:
        - Employs a hybrid method combining linear interpolation (the basis of the Secant Method) and binary search to find the most efficient (highest) CRF value that satisfies the target VMAF score.
          - It first predicts the next search point using linear interpolation to accelerate convergence. If the prediction falls out of bounds, it safely switches to a stable binary search.

        **LaTeX Formula (Linear Interpolation)**
        ```math
        q_{\text{next}} = q_{\text{high}} + (q_{\text{low}} - q_{\text{high}}) \times \frac{v_{\text{target}} - v_{\text{low}}}{v_{\text{high}} - v_{\text{low}}}
        ```
        **Plain Code Logic**
        ```
        q_next = q_high + (q_low - q_high) * (v_target - v_low) / (v_high - v_low)
        
        // If q_next is outside the [q_low, q_high] range,
        // fall back to binary search: q_next = q_low + (q_high - q_low) / 2
        ```
  
    <br>

    -   **Pareto Front Calculation (Multi-objective Optimization)**:
        -   Identifies the set of optimal results that are not 'dominated' by any other result. Result `A` dominates result `B` under the following conditions:
        -   **Dominance Conditions**:
            1.  `A` is no worse than `B` in all optimization criteria.
            2.  `A` is strictly better than `B` in at least one criterion.
            3.  **Tie-Breaker**: If all numerical metrics are identical, the one with the faster preset (e.g., `fast` vs. `slow`) is considered superior.
          
            **LaTeX Formula**
            ```math
            (\text{VMAF}(A) \ge \text{VMAF}(B) \land \text{size}(A) \le \text{size}(B))
            \land
            (\text{VMAF}(A) > \text{VMAF}(B) \lor \text{size}(A) < \text{size}(B))
            ```
            **Plain Code Logic**
            ```
            (A.vmaf >= B.vmaf AND A.size <= B.size)
            AND
            (A.vmaf > B.vmaf OR A.size < B.size)
            // If the above conditions are all false (i.e., all values are equal)
            // OR (A.preset_speed > B.preset_speed)
            ```

<br>

## 🔄 Changelog

### v1.0.1 (2025-09-06)

This update focuses on improving the stability and UI clarity of the manual sample mode, based on user feedback.

-   #### **Bug Fixes**
    -   **Improved Manual Sample Mode Stability**:
        -   Fixed an issue where encoding tests would not run correctly when `Sample Selection` was set to `Manual` due to an internal settings conflict. The manually specified sample range is now reliably applied to all tests.

-   #### **Improvements**
    -   **Enhanced UI Clarity**:
        -   The `Analysis Method` dropdown menu, which is irrelevant in `Manual` mode, is now correctly disabled when this mode is selected. This prevents user confusion and improves UI consistency.

<br>

<details>
<summary>📜 Previous Updates - Click to expand</summary>
<br>
<details>
<summary>v1.0.0 (2025-09-04)</summary>

-   Initial release.

</details>
</details>

<br>

## 📄 License

This project is licensed under the **[GNU General Public License v3.0](LICENSE)**.
