# Monocular 3D object detection을 이용한 depth 인식 시스템

## 이용 모델

GUPNet:
높이 기반으로 depth를 예측하는 방식, 오차를 줄이기 위해 분포로 3d 높이와 depth를 추론
    @article{lu2021geometry,
    title={Geometry Uncertainty Projection Network for Monocular 3D Object Detection},
    author={Lu, Yan and Ma, Xinzhu and Yang, Lei and Zhang, Tianzhu and Liu, Yating and Chu, Qi and Yan, Junjie and Ouyang, Wanli},
    journal={arXiv preprint arXiv:2107.13774},year={2021}}

Monocular 3D object detection:
   3D 이미지에서 객체 주위에 3d bounding box를 그리는 작업
   
## 연구내용
학습된 log를 가지고 test를 진행, 추론한 depth를 바탕으로 3d bounding box로 근거리 위험성을 한눈에 볼 수 있도록 함

# project_CSEgrad
