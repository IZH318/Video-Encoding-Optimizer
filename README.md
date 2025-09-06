# Video Encoding Optimizer

<p align="center">
  <img src="https://img.shields.io/badge/Windows-8.1%2B-0078D6.svg?style=flat-square&logo=windows&logoColor=white" alt="OS: Windows 8.1+">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square" alt="License: GPL v3">
  <img src="https://img.shields.io/badge/Powered%20by-FFmpeg-4E963A.svg?style=flat-square&logo=ffmpeg&logoColor=white" alt="Powered by FFmpeg">
</p> <br>

<img width="802" height="652" alt="캡처_2025_09_04_05_56_43_601" src="https://github.com/user-attachments/assets/b90500b7-27c6-4dc4-ad5b-eea3a382a6a4" /> <br>

**최적의 비디오 인코딩 설정을 찾기 위한 GUI 애플리케이션** <br>
다양한 코덱과 설정을 테스트하여 화질(VMAF), 파일 크기, 인코딩 속도 간의 최적의 균형점을 찾아주는 애플리케이션입니다. <br>
복잡한 FFmpeg 명령어를 직접 다루지 않고도, 데이터 기반의 합리적인 결정을 내릴 수 있도록 돕습니다. <br> <br>


**영문 버전의 README는 [README_EN.md](./README_EN.md)에서 확인하실 수 있습니다.** <br>
**You can find the English version of the README in [README_EN.md](./README_EN.md).**

<br>

## 🖼️ 미리보기 (Preview)

### 1. 메인 인터페이스 (Main UI)
<img width="802" height="652" alt="캡처_2025_09_04_04_13_09_118" src="https://github.com/user-attachments/assets/b31a63b0-65a1-44c0-9bf4-7a0f4e258eb7" />

> 단일 창 인터페이스에서 코덱 선택, 최적화 모드 설정, 샘플링 방식 지정 등 모든 핵심 기능을 제어하고, 실시간으로 분석 결과를 확인할 수 있습니다.

<br>

### 2. 상호작용형 그래프 (Interactive Graph)
<img width="902" height="732" alt="캡처_2025_09_04_04_22_13_133" src="https://github.com/user-attachments/assets/07077e21-938b-431e-9c0f-338e4e57f82b" />

> 모든 인코딩 결과를 2D 산점도로 시각화하여 데이터의 상관관계를 직관적으로 분석할 수 있습니다.
> 
> X/Y축을 자유롭게 변경하고, 확대/축소/이동하며 데이터를 심층적으로 탐색할 수 있습니다.

<br>

### 3. A/B 비교 (A/B Comparison)
**▼ 원본 영상 샘플 (Original Sample)** <br>
<img width="1920" height="1080" alt="original_sample mkv_snapshot_00 07 006" src="https://github.com/user-attachments/assets/1b573ffa-d91f-4d82-b7ed-0f943e3f4509" />

> 비교의 기준이 되는 원본 영상의 한 장면입니다.
<details>
<summary>📄 원본 영상 파일 MediaInfo 정보 상세보기</summary>

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
Stream size                    : 390 MiB (5%)```
```
</details>

<br>

이제 두 가지 인코딩 설정을 비교해 보겠습니다. 두 설정 모두 아래와 같은 공통된 조건에서 진행되었습니다.
- **Encoder Group**: `Software`
- **Codec**: `libx264`
- **Sample Selection**: `Auto (Complex Scene)`
- **Durations (s)**: `7`
- **Analysis Method**: `Single-Point`

<br>

**▼ 차이 A (Difference A) - *Preset: fast, CRF: 21*** <br>
<img width="1920" height="1080" alt="diff_A_fast_21_vs_Original mkv_snapshot_00 07 006" src="https://github.com/user-attachments/assets/eced6aad-9eed-4c18-a0f1-e46a7d9266c7" />

<br>

**▼ 차이 B (Difference B) - *Preset: ultrafast, CRF: 51*** <br>
<img width="1920" height="1080" alt="diff_B_ultrafast_51_vs_Original mkv_snapshot_00 07 006" src="https://github.com/user-attachments/assets/cb0f4126-0c7f-437f-9635-0165a40a43a9" />

> 위 두 이미지는 각각 **설정 A**와 **설정 B**가 원본 영상과 얼마나 다른지를 시각화한 결과입니다.
>
> **차이 A**는 일부 윤곽선만 희미하게 보이는 반면, **차이 B**는 A에 비해 훨씬 밝고 뚜렷한 윤곽선이 나타납니다.
> 
> 이는 설정 B에서 더 많은 정보 손실이 발생했음을 의미하며, **설정 A가 원본을 더 잘 보존한 우수한 결과**임을 알 수 있습니다.

<br>

### 4. 상세 HTML 리포트 (HTML Report)
![screencapture-file-C-Users-Administrator-Desktop-Video-Encoding-Optimizer-Resource-ep11test-html-2025-09-04-04_48_58 (Resize)](https://github.com/user-attachments/assets/5a63eadf-7cf2-4301-872a-5daaaab5bda9)

> 모든 분석 결과, 테스트 파라미터, 추천 설정, 그리고 Chart.js 기반의 상호작용형 그래프까지 하나의 HTML 파일로 내보낼 수 있습니다.
> 
> 이 리포트는 분석 내용을 보관하거나 다른 사람과 공유하는 데 매우 유용합니다.

<br>

## 🌟 주요 기능 (Key Features)

-   **폭넓은 코덱 지원**:
    -   **소프트웨어**: `libx264`, `libx265`, `libaom-av1`, `svt-av1`, `librav1e` 등
    -   **하드웨어 가속**: NVIDIA (NVENC), Intel (QSV), AMD (AMF)를 통한 H.264/HEVC/AV1 인코딩을 완벽히 지원합니다.
-   **자동화된 샘플 추출 및 분석**:
    -   **지능형 장면 탐지**: 영상에서 가장 복잡하거나(complex) 단순한(simple) 장면을 자동으로 찾아내어 테스트 샘플로 추출합니다. 사용자는 분석 속도 향상을 위해 병렬/순차 분석 방식을 선택할 수 있습니다.
    -   **정확한 품질 측정**: VMAF를 기본으로, PSNR, SSIM, 블록 스코어 등 다양한 품질 메트릭을 정밀하게 분석합니다.
-   **강력한 병렬 처리**:
    -   멀티프로세싱을 활용하여 여러 인코딩 작업을 동시에 실행, 분석 시간을 획기적으로 단축합니다. (시스템의 물리 CPU 코어 수 기반)
-   **두 가지 고급 최적화 모드**:
    -   **범위 테스트 (Range Test)**: 지정된 프리셋과 품질(CRF/CQ/QP) 범위 내의 모든 조합을 테스트하여 전체적인 성능 분포를 파악합니다.
    -   **목표 VMAF (Target VMAF)**: 설정한 VMAF 점수를 만족하는 가장 효율적인(가장 높은 CRF 값) 설정을 각 프리셋별로 지능적으로 탐색하며, 이 탐색 작업들은 병렬로 실행되어 속도를 극대화합니다.
-   **심층적인 결과 분석 및 시각화**:
    -   **상호작용형 그래프**: 모든 테스트 결과를 `Chart.js` 기반의 2D 산점도로 시각화하며, X/Y축을 자유롭게 변경하여 다양한 관점에서 데이터를 분석할 수 있습니다.
    -   **파레토 프론트 (Pareto Front)**: 어떤 다른 설정보다 모든 면에서 우월한, 가장 효율적인 인코딩 옵션들을 자동으로 하이라이트합니다.
    -   **스위트 스팟 (Sweet Spot)**: Pareto Front 결과 중에서 품질과 파일 크기 간의 가장 균형 잡힌 '가성비' 지점을 자동으로 추천합니다.
-   **안정적인 포맷 처리**:
    -   **방송용 포맷(M2TS, TS) 고급 지원**: 방송용 스트림에서 흔히 발생하는 타임스탬프 오프셋(PTS offset)을 자동으로 보정하고, 인터레이스 영상을 감지하여 분석에 적합하도록 자동으로 디인터레이싱합니다.
    -   **색상 정보 보존**: 원본 비디오의 색상 메타데이터(Color Space, Range, Primaries 등)를 감지하여 인코딩 시 명시적으로 적용, HDR/SDR 영상의 색상 왜곡을 방지합니다.
    -   **동적 파일 지원**: FFmpeg가 지원하는 거의 모든 비디오 포맷을 자동으로 인식하여 파일 선택 대화상자에 표시합니다.
-   **사용자 편의 기능**:
    -   **FFmpeg 자동 다운로드 및 설정**: 애플리케이션 실행 시 FFmpeg가 없으면 자동으로 최신 버전을 다운로드하고 설정합니다.
    -   **VMAF 모델 관리**: Netflix의 공식 VMAF 모델들을 클릭 한 번으로 다운로드하고 테스트에 적용할 수 있습니다.
    -   **A/B 비교 샘플 생성**: 두 개의 결과물을 선택하여 원본과 나란히 비교할 수 있는 샘플 비디오와 차이(difference) 비디오를 즉시 생성합니다.
    -   **최종 명령어 생성**: 선택한 최적의 설정을 전체 비디오에 적용할 수 있는 FFmpeg 명령어를 자동으로 생성하고 클립보드에 복사할 수 있습니다.
    -   **상세 리포트 내보내기**: 모든 분석 결과를 CSV 데이터 또는 상호작용형 그래프가 포함된 상세한 단일 HTML 리포트로 저장할 수 있습니다.

<br>

## ⚙️ 작동 원리 (How it Works)

이 도구는 다음과 같은 체계적인 프로세스를 통해 최적의 인코딩 설정을 찾아냅니다.

1.  **1단계: 지능형 샘플 추출 (Intelligent Sample Extraction)**
    -   사용자가 '자동' 모드를 선택하면, FFprobe를 사용하여 비디오 전체를 빠르게 스캔합니다. 이 과정에서 각 프레임의 **데이터 크기(`pkt_size`)** 를 분석하여 장면의 복잡도를 측정합니다. 사용자는 **병렬 분석**과 **순차 분석** 중 선택할 수 있습니다.
    -   **복잡한 장면 (Complex Scene)**: **초당 데이터 크기의 합이 가장 큰 구간**을 찾아냅니다. 이 구간은 움직임과 디테일이 많아 비트레이트가 가장 많이 요구되는 부분으로, 코덱의 디테일 보존 능력과 성능 한계를 테스트하기에 적합합니다.
    -   **단순한 장면 (Simple Scene)**: **초당 데이터 크기의 합이 가장 작은 구간**을 찾아냅니다. 이 구간은 주로 정적이고 평탄한 영역으로, 낮은 비트레이트에서 블록킹(깍두기 현상)이 발생하기 쉬워 코덱의 압축 효율성을 평가하기 좋습니다.
    -   **분석 방식 (Analysis Method)**: 최적의 구간을 찾는 데 두 가지 알고리즘을 선택할 수 있습니다.
        -   **Sliding Window (슬라이딩 윈도우)**: 초당 데이터 크기 맵 전체에 걸쳐 설정된 샘플 길이(`Duration`)만큼의 '창(window)'을 이동시키며 각 창의 **평균 복잡도**를 계산합니다. 이 방식은 순간적인 피크가 아닌, 지속적으로 복잡도가 높은(또는 낮은) **'구간'** 전체를 찾아내므로 더 안정적이고 대표성 있는 샘플을 추출할 수 있습니다.
        -   **Single-Point (단일 지점)**: 가장 복잡도가 높은(또는 낮은) **단일 1초 지점**을 찾고, 그 시간을 중심으로 샘플을 구성합니다. 슬라이딩 윈도우 계산을 생략하므로 분석이 더 빠르지만, 순간적인 데이터 스파이크를 선택하여 영상 전체의 특성을 제대로 반영하지 못할 위험이 있습니다.
    -   찾아낸 구간은 원본 품질을 그대로 보존하기 위해 무손실(lossless) 코덱으로 빠르게 추출되어 임시 파일로 저장됩니다. 특히, M2TS와 같은 방송용 포맷의 경우 타임스탬프 오프셋을 자동으로 보정하고 인터레이스 영상을 감지하는 등 추가적인 전처리 과정을 거칩니다.

2.  **2단계: 병렬 인코딩 및 분석 (Parallel Encoding & Analysis)**
    -   사용자가 설정한 모든 테스트 조합에 대한 `EncodingTask` 객체 리스트를 생성합니다. 이때 원본 비디오의 색상 정보를 미리 추출하여 각 Task에 포함시킵니다.
    -   Python의 `multiprocessing.Pool`을 사용하여 시스템의 물리 CPU 코어 수에 맞춰 여러 개의 워커(worker) 프로세스를 생성합니다.
    -   각 워커 프로세스는 독립적으로 `EncodingTask`를 받아 FFmpeg를 실행하여 샘플을 인코딩하고, VMAF, PSNR, SSIM 등의 품질 메트릭을 계산합니다. 이 병렬 처리 덕분에 **'Range Test'** 모드에서는 수십 개의 테스트를, **'Target VMAF'** 모드에서는 여러 프리셋에 대한 탐색을 동시에 진행할 수 있습니다.

3.  **3단계: 결과 집계 및 심층 분석 (Result Aggregation & In-depth Analysis)**
    -   모든 워커로부터 반환된 결과(VMAF 점수, 파일 크기 등)는 메인 스레드로 비동기적으로 전달되어 UI에 실시간으로 업데이트됩니다.
    -   모든 테스트가 완료되면, 다음과 같은 고급 분석이 수행됩니다.
        -   **Pareto Front 계산**: 파일 크기와 VMAF 점수를 두 축으로 하여, 다른 어떤 결과물에도 '지배'당하지 않는(즉, 더 낮은 파일 크기에 더 높은 VMAF 점수를 가진 결과가 없는) 최적의 결과물 집합을 식별합니다.
        -   **Sweet Spot 탐색**: 계산된 Pareto Front에서, 그래프의 시작점과 끝점을 잇는 가상의 직선으로부터 가장 멀리 떨어진 점을 탐색합니다. 이 점은 일반적으로 품질과 파일 크기 간의 균형이 가장 잘 맞는 '무릎 지점(knee point)'에 해당하며, 가장 균형 잡힌 설정으로 추천됩니다.

4.  **4단계: 시각화 및 최종 결과 제공 (Visualization & Final Output)**
    -   분석된 모든 데이터는 Matplotlib과 Chart.js를 통해 상호작용 가능한 그래프로 시각화됩니다. 사용자는 X축과 Y축을 원하는 메트릭으로 변경하며 데이터의 상관관계를 직관적으로 파악할 수 있습니다.
    -   사용자는 결과 테이블이나 그래프에서 가장 마음에 드는 설정을 선택하여, 전체 비디오에 적용할 수 있는 최종 FFmpeg 명령어를 생성할 수 있습니다.

<br>

## 🚀 설치 및 사용법 (Installation & Usage)

### 요구사항
-   **운영 체제**: Windows 8.1 이상
-   **Python**: 3.10 이상 [[**Download**]](https://www.python.org/downloads/windows/)

<br>

### 설치 (Installation)
1.  [**Releases**](https://github.com/IZH318/Video-Encoding-Optimizer/releases)에서 최신 버전의 파일을 다운로드합니다.
2.  프로젝트 디렉토리에서 터미널을 열고, 다음 두 가지 방법 중 하나를 선택하여 필요한 라이브러리를 설치합니다.

    **방법 A: 직접 설치**
    ```bash
    pip install matplotlib psutil requests
    ```

    **방법 B: `requirements.txt` 파일 사용**
    ```bash
    pip install -r requirements.txt
    ```
3.  `Video Encoding Optimizer.py`를 실행합니다.

<br>

### 상세 사용 가이드

#### 1. 비디오 파일 선택
-   `Select Video...` 버튼을 클릭하여 분석할 비디오 파일을 선택합니다.

<br>

#### 2. 인코딩 설정

-   **Encoder Group & Codec**:
    -   애플리케이션이 시스템에 설치된 인코더를 자동으로 감지하여 그룹(Software, NVENC 등)으로 보여줍니다.
    -   원하는 그룹을 선택하면 해당 그룹에 속하는 코덱 목록(예: `libx265`, `hevc_nvenc`)이 나타납니다. 코덱을 선택하세요.
-   **Preset Range**:
    -   테스트할 인코딩 속도/압축률 프리셋의 범위를 지정합니다. 예를 들어 `fast`부터 `veryslow`까지 선택하면 그 사이의 모든 프리셋(`fast`, `medium`, `slow`, `slower`, `veryslow`)이 테스트 대상에 포함됩니다.
-   **Optimization Mode**:
    -   **Range Test**: 지정한 품질(CRF/CQ) 값의 시작과 끝 범위를 모두 테스트합니다. 예를 들어 CRF 18-22로 설정하면 18, 19, 20, 21, 22를 모두 테스트합니다.
    -   **Target VMAF**: 목표 VMAF 점수를 설정하면, 각 프리셋별로 해당 점수를 만족하는 가장 효율적인(CRF 값이 가장 높은) 설정을 지능적으로 찾아냅니다. 이 모드는 각 프리셋의 탐색을 병렬로 동시에 처리하여 분석 효율을 극대화합니다.
-   **Audio**:
    -   오디오를 원본 그대로 복사(`Copy Audio`)할지, 제거(`Remove Audio`)할지 선택합니다.
-   **병렬 작업 및 NVENC 경고**: 'Parallel Jobs' 수를 조절할 수 있습니다. NVENC 코덱 사용 시 이 값이 하드웨어 제한을 초과하면 오류가 발생할 수 있습니다.
    -   NVIDIA의 공식 정책에 따라, 대부분의 GeForce 계열 GPU는 동시에 실행 가능한 인코딩 세션 수가 드라이버 레벨에서 제한됩니다.
        -   정확한 정보는 [[**NVIDIA 공식 비디오 인코딩/디코딩 GPU 지원 매트릭스**]](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new) 에서 확인.

<br>

#### 3. 샘플 선택

-   **Auto (자동)**:
    -   **Complex Scene**: 디테일이 많고 복잡한 장면을 자동으로 찾아 테스트합니다. 코덱의 디테일 보존 능력을 평가하기에 좋습니다.
    -   **Simple Scene**: 색상 변화가 적고 평탄한 장면을 찾아 테스트합니다. 낮은 비트레이트에서 발생하는 블록킹 현상을 평가하기에 좋습니다.
    -   `Duration (s)`: 추출할 샘플의 길이를 초 단위로 설정합니다.
-   **Analysis Method**:
    -   `Sliding Window` (기본값): 설정한 `Duration` 길이의 '구간'을 통째로 분석하여 가장 대표적인 장면을 찾습니다. 더 안정적이고 신뢰도 높은 분석이 가능합니다.
    -   `Single-Point`: 가장 복잡도가 높은(또는 낮은) '순간'(1초)을 찾아 그 지점을 중심으로 샘플을 구성합니다. 분석 속도는 더 빠르지만, 영상 전체를 대표하지 못할 수 있습니다.
-   **Manual (수동)**:
    -   `Set Range...` 버튼을 눌러 시:분:초.밀리초 형식으로 샘플의 시작과 끝 시간을 직접 지정할 수 있습니다.
-   **Sample Preview**: `ffplay`를 사용하여 현재 설정된 샘플 구간을 미리 재생해볼 수 있습니다.

<br>

#### 4. 고급 설정 및 추가 옵션

-   **Advanced Settings...**: 현재 선택된 코덱에 특화된 고급 옵션(예: `aq-mode`, `psy-rd`, `lookahead` 등)을 세밀하게 조정할 수 있는 별도의 창이 열립니다. 각 옵션에는 툴팁 설명이 제공됩니다.
-   **Add Metrics**: VMAF 외에 PSNR, SSIM, Block Score를 추가로 계산할지 여부를 선택합니다. 약간의 추가 분석 시간이 소요됩니다.
-   **VMAF Model**: `Download/Update Models` 버튼으로 공식 VMAF 모델들을 다운로드한 후, `Browse...` 버튼을 통해 특정 해상도나 기기에 최적화된 모델(예: `vmaf_4k_v0.6.1.json`)을 선택하여 분석에 사용할 수 있습니다.

<br>

#### 5. 최적화 시작
-   모든 설정을 마친 후 `Start Optimization` 버튼을 누르면 분석이 시작됩니다. 진행률 표시줄과 상태 메시지를 통해 현재 진행 상황을 확인할 수 있습니다.
-   `Cancel` 버튼을 누르면 진행 중인 모든 작업을 즉시 중단합니다.

<br>

#### 6. 결과 확인 및 활용

-   **Results Table**:
    -   모든 테스트 결과가 표에 실시간으로 추가됩니다. 컬럼 헤더를 클릭하여 결과를 정렬할 수 있습니다.
    -   **색상 하이라이트**:
        -   🟡 **Sweet Spot**: 품질과 파일 크기 간의 균형이 가장 이상적인 추천 설정입니다.
        -   🟢 **Pareto Optimal**: 효율적인 설정들입니다. 이들보다 더 좋다고 말할 수 있는 다른 설정은 없습니다.
        -   🟣 **Lowest VMAF**: 테스트 중 가장 낮은 VMAF 점수를 기록한 설정입니다.
        -   🔴 **Least Efficient**: 가장 비효율적인(VMAF/MB가 가장 낮은) 설정입니다.

-   **결과 활용 버튼**:
    -   **View Graph**: 결과를 상호작용형 그래프로 봅니다. 마우스 휠로 확대/축소, 드래그로 이동이 가능하며, 점 위에 마우스를 올리면 상세 정보가 툴팁으로 표시됩니다.
    -   **A/B Compare**: 테이블에서 두 개의 결과를 선택한 후 이 버튼을 누르면, 해당 설정으로 인코딩된 두 개의 샘플 영상과 원본과의 차이를 보여주는 'Difference' 영상이 생성되어 폴더에 저장됩니다. 시각적으로 품질 차이를 비교하는 데 매우 유용합니다.
    -   **View Command**: 테이블에서 하나의 결과를 선택하면, 해당 설정을 전체 비디오에 적용하는 데 필요한 `ffmpeg` 명령어를 생성하여 보여줍니다.
    -   **View Log**: 선택한 결과의 인코딩 및 분석 과정에서 생성된 전체 `ffmpeg` 로그를 확인할 수 있어, 문제 해결에 도움이 됩니다.
    -   **Export Results**: 모든 결과를 CSV 파일이나, 모든 정보와 상호작용형 그래프가 포함된 단일 HTML 파일로 내보낼 수 있습니다.

<br>

## 🔧 핵심 메커니즘 분석 (Analysis of Core Mechanisms)

-   **아키텍처**:
    -   `VideoOptimizerApp` 클래스가 메인 GUI와 애플리케이션 로직을 관리합니다.
    -   `EncodingTask` 데이터 클래스는 각 인코딩 작업에 필요한 모든 파라미터를 구조화합니다.
    -   `FFmpegCommandBuilder` 클래스는 `EncodingTask`를 기반으로 동적으로 FFmpeg 명령어를 생성하여 코드의 재사용성과 유지보수성을 높입니다.
    -   `perform_one_test` 함수는 단일 `EncodingTask`를 처리하도록 설계되었으며, `multiprocessing`을 통해 별도의 프로세스에서 실행됩니다. 이는 GIL(Global Interpreter Lock)의 제약을 우회하여 CPU 집약적인 인코딩 작업을 완벽하게 병렬화합니다.

<br>

-   **지능형 장면 탐색 (Intelligent Scene Detection)**:
    -   **Frame Size Analysis**: 복잡한 장면 탐색 시, FFprobe를 통해 추출한 프레임별 **패킷 크기(`pkt_size`)** 를 분석합니다. 이 데이터 크기는 장면의 복잡도(모션, 디테일)와 직접적인 관련이 있어, 가장 데이터량이 많거나 적은 구간을 효과적으로 찾아낼 수 있습니다.
    -   **Two-Pass Hybrid Parallel Analysis**: 사용자가 병렬 분석을 선택하면, 1차로 비디오 전체를 빠르게 스캔하여 키프레임(I-frame)의 타임스탬프만 추출합니다. 2차로 이 타임스탬프 목록을 기준으로 분석 구간을 나누어 각 CPU 코어에 할당, 모든 프레임을 병렬로 상세 분석하여 디스크 I/O 경합을 최소화하고 속도를 극대화합니다.

<br>

-   **동적 UI 생성 및 확장성**:
    -   `CODEC_CONFIG` 딕셔너리는 모든 코덱의 설정(프리셋, 품질 범위, 고급 옵션 등)을 중앙에서 관리하는 스키마 역할을 합니다.
    -   `AdvancedSettingsWindow`는 이 스키마를 읽어 각 코덱에 맞는 UI 위젯(콤보박스, 스핀박스, 체크박스 등)을 동적으로 생성하여, 새로운 코덱이나 옵션을 쉽게 추가할 수 있는 확장성 높은 구조를 가집니다.

<br>

-   **안정적인 미디어 처리**:
    -   **색상 보존 (Color Preservation)**: `get_color_info` 함수가 FFprobe를 통해 원본 비디오의 색상 메타데이터(Color Space, Range, Primaries, TRC)를 추출하고, 이를 각 인코딩 명령어에 명시적으로 추가합니다. 이로써 색상 변환 과정에서 발생할 수 있는 왜곡을 방지하고 원본의 색감을 정확하게 유지합니다.
    -   **방송용 스트림 처리 (Broadcast Stream Handling)**: M2TS/TS 스트림의 PTS(Presentation Time Stamp) 오프셋을 자동으로 감지하고 모든 타임스탬프가 0부터 시작하도록 정규화합니다. 또한, 인터레이스 영상을 감지하여 `bwdif` 필터로 자동 디인터레이싱 후 분석을 진행하여 정확도를 높입니다.
    -   **A/B 비교**: `blend=all_mode=difference` 필터를 사용하여 두 영상 간의 픽셀 단위 차이를 시각화하는 'Difference' 영상을 생성합니다.

<br>

-   **핵심 분석 지표 및 알고리즘**:
    -   **IQR 이상치 제거 (IQR Outlier Removal)**:
        - 장면 분석 시, 순간적인 데이터 오류(예: 손상된 프레임)나 극단적인 값들이 전체 분석 결과를 왜곡하는 것을 방지합니다.
          - 통계 기법인 **사분위수 범위(Interquartile Range)** 를 사용하여 정상 범위를 벗어나는 데이터를 이상치로 간주하고 제거합니다.
          - 특히, 코드에서는 일반적인 Q1(25%), Q3(75%) 대신 **하위 15%와 상위 85%** 를 기준으로 사용하여 더 안정적인 분석을 수행합니다.

        **LaTeX 공식**
        ```math
        \text{IQR} = Q_{0.85} - Q_{0.15} \\
        \text{Lower Bound} = Q_{0.15} - (k \times \text{IQR}) \\
        \text{Upper Bound} = Q_{0.85} + (k \times \text{IQR})
        ```
        *(여기서 k는 이상치 탐색의 민감도를 조절하는 승수로, 코드에서는 3.0을 사용합니다.)*

        **논리 표현식 (Plain Code)**
        ```
        IQR = Percentile(Data, 85) - Percentile(Data, 15)
        Lower_Bound = Percentile(Data, 15) - (3.0 * IQR)
        Upper_Bound = Percentile(Data, 85) + (3.0 * IQR)
        
        // 데이터가 Lower_Bound와 Upper_Bound 사이에 있을 때만 유효한 것으로 간주
        Valid_Data = {d | d for d in dataset if Lower_Bound <= d <= Upper_Bound}
        ```

    <br>

    -   **하위 1% VMAF (VMAF 1% Low)**:
        - 전체 영상의 평균 VMAF 점수만으로는 파악하기 힘든 '품질 일관성'을 측정합니다.
          - 평균 점수는 높아도 특정 구간에서 품질이 급격히 저하되는 경우를 잡아내기 위한 지표입니다.
          - 모든 프레임의 VMAF 점수를 정렬한 후, 하위 1%에 해당하는 점수들의 평균을 계산합니다.
        
        **LaTeX 공식**
        ```math
        S = \{v_1, v_2, \dots, v_n\} \quad (\text{단, } v_i \le v_{i+1}) \\
        N_{1\%} = \lfloor n \times 0.01 \rfloor \\
        \text{VMAF}_{1\%\text{ Low}} = \frac{1}{N_{1\%}+1} \sum_{i=1}^{N_{1\%}+1} v_i
        ```
        **논리 표현식 (Plain Code)**
        ```
        All_VMAF_Scores = sorted([...])
        One_Percent_Index = floor(length(All_VMAF_Scores) * 0.01)
        
        // 하위 1%에 해당하는 점수들 (최소 1개 포함)
        Lowest_Scores = All_VMAF_Scores[0 ... One_Percent_Index]
        
        VMAF_1_Percent_Low = average(Lowest_Scores)
        ```

    <br>

    -   **효율성 지표 (Efficiency Metric)**:
        - 인코딩 설정의 '가성비'를 정량적으로 평가하기 위한 핵심 지표로, **VMAF 점수 / 파일 크기(MB)** 공식을 사용합니다.
          - 1MB 용량당 얼마나 높은 VMAF 품질을 얻었는지를 나타냅니다.

        **LaTeX 공식**
        ```math
        \text{Efficiency} = \frac{\text{VMAF}_{\text{mean}}}{\text{File Size (MB)}}
        ```
        **논리 표현식 (Plain Code)**
        ```
        Efficiency = VMAF_Score / File_Size_in_MB
        ```

    <br>

    -   **'Sweet Spot' 탐색 알고리즘 (Perpendicular Distance Heuristic)**:
        - Pareto Front 결과들 중에서 품질과 파일 크기 간의 가장 균형 잡힌 지점을 찾기 위해, 기하학적 휴리스틱을 사용합니다.
          - Pareto Front의 시작점 `P₁(size₁, vmaf₁)`과 끝점 `P₂(size₂, vmaf₂)`을 잇는 직선으로부터 가장 멀리 떨어진 점 `P₀(size₀, vmaf₀)`를 찾습니다.

        **LaTeX 공식**
        ```math
        d = \frac{|(y_2 - y_1)x_0 - (x_2 - x_1)y_0 + x_2y_1 - y_2x_1|}{\sqrt{(y_2 - y_1)^2 + (x_2 - x_1)^2}}
        ```
        *실제 코드에서는 분모(denominator)가 모든 점에 대해 동일한 상수이므로, 연산 속도를 위해 분자(numerator) 값만 계산하여 최대가 되는 지점을 찾습니다.*
        
        **논리 표현식 (Plain Code)**
        ```
        P_start = (size_min, vmaf_at_min)
        P_end = (size_max, vmaf_at_max)
        
        // 모든 Pareto Front 점 P_current에 대해 아래 값을 계산
        P_current = (current_size, current_vmaf)
        
        // 점과 직선 사이의 거리 공식의 분자 부분
        distance_numerator = abs(
            (P_end.y - P_start.y) * P_current.x - 
            (P_end.x - P_start.x) * P_current.y + 
            P_end.x * P_start.y - P_end.y * P_start.x
        )
        
        // 'distance_numerator'를 최대화하는 P_current가 Sweet Spot이 됨
        SweetSpot = Point P_current that maximizes the distance_numerator
        ```

    <br>

    -   **'Target VMAF' 탐색 알고리즘 (하이브리드 탐색)**:
        - 목표 VMAF 점수를 만족하는 가장 효율적인(가장 높은) CRF 값을 찾기 위해 선형 보간(Secant Method의 근간)과 이진 탐색을 결합한 하이브리드 방식을 사용합니다.
          - 먼저 선형 보간으로 다음 탐색 지점을 예측하여 수렴 속도를 높이고, 예측값이 범위를 벗어날 경우 안정적인 이진 탐색으로 안전하게 전환합니다.

        **LaTeX 공식 (선형 보간)**
        ```math
        q_{\text{next}} = q_{\text{high}} + (q_{\text{low}} - q_{\text{high}}) \times \frac{v_{\text{target}} - v_{\text{low}}}{v_{\text{high}} - v_{\text{low}}}
        ```
        **논리 표현식 (Plain Code)**
        ```
        q_next = q_high + (q_low - q_high) * (v_target - v_low) / (v_high - v_low)
        
        // 만약 q_next가 [q_low, q_high] 범위를 벗어나면, 
        // q_next = q_low + (q_high - q_low) / 2 로 대체 (이진 탐색)
        ```
  
    <br>

    -   **Pareto Front 계산 (다기준 최적화)**:
        -   어떤 다른 결과물에도 '지배(dominate)'당하지 않는 최적의 결과 집합을 식별합니다. 결과 `A`가 결과 `B`를 지배하는 조건은 다음과 같습니다.
        -   **지배(Dominance) 조건**:
            1.  모든 최적화 기준에서 `A`가 `B`보다 나쁘지 않다.
            2.  최소 하나의 최적화 기준에서 `A`가 `B`보다 명백히 우수하다.
            3.  **Tie-Breaker**: 모든 수치 지표가 동일할 경우, 더 빠른 프리셋(예: `fast` vs `slow`)을 가진 쪽이 우수한 것으로 간주합니다.
          
            **LaTeX 공식**
            ```math
            (\text{VMAF}(A) \ge \text{VMAF}(B) \land \text{size}(A) \le \text{size}(B))
            \land
            (\text{VMAF}(A) > \text{VMAF}(B) \lor \text{size}(A) < \text{size}(B))
            ```
            **논리 표현식 (Plain Code)**
            ```
            (A.vmaf >= B.vmaf AND A.size <= B.size)
            AND
            (A.vmaf > B.vmaf OR A.size < B.size)
            // 만약 위 조건이 모두 false(즉, 모든 값이 같다면)
            // OR (A.preset_speed > B.preset_speed)
            ```

<br>

## 🔄 업데이트 내역

### v1.0.1 (2025-09-06)

이번 업데이트는 사용자 피드백을 반영하여 수동 샘플 모드의 안정성과 UI 명확성을 개선하는 데 중점을 두었습니다.

-   #### **버그 수정 (Bug Fixes)**
    -   **수동 샘플 모드 안정성 향상**:
        -   `Sample Selection`을 `Manual` 모드로 설정했을 때, 내부 설정값 충돌로 인해 인코딩 테스트가 올바르게 동작하지 않던 문제를 수정했습니다. 이제 수동으로 지정한 샘플 구간이 모든 테스트에 안정적으로 적용됩니다.

-   #### **개선 사항 (Improvements)**
    -   **UI 명확성 개선**:
        -   `Manual` 모드 선택 시, 관련 없는 설정인 `Analysis Method` 드롭다운 메뉴가 명확하게 비활성화되도록 변경했습니다. 이를 통해 사용자 혼란을 방지하고 UI의 일관성을 높였습니다.

<br>

<details>
<summary>📜 이전 업데이트 내역 - 클릭하여 열기</summary>
<br>
<details>
<summary>v1.0.0 (2025-09-04)</summary>

-   최초 릴리스.

</details>
</details>

<br>

## 📄 라이선스 (License)

이 프로젝트는 **[GNU General Public License v3.0](LICENSE)** 에 따라 라이선스가 부여됩니다.
