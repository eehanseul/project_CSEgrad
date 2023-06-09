import os
import tqdm

import torch, cv2
import numpy as np
import time

from lib.helpers.save_helper import load_checkpoint
from lib.helpers.decode_helper import extract_dets_from_outputs
from lib.helpers.decode_helper import decode_detections

class Tester(object):
    
    def __init__(self, cfg, model, data_loader, logger):
        self.cfg = cfg
        self.model = model
        self.data_loader = data_loader
        self.logger = logger
        self.class_name = data_loader.dataset.class_name
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        if self.cfg.get('resume_model', None):
            load_checkpoint(model = self.model,
                        optimizer = None,
                        filename = cfg['resume_model'],
                        logger = self.logger,
                        map_location=self.device)

        self.model.to(self.device)

    def test(self):
        
        torch.set_grad_enabled(False)
        self.model.eval()
        
        results = {}
        progress_bar = tqdm.tqdm(total=len(self.data_loader), leave=True, desc='Evaluation Progress')
        

        for batch_idx, (inputs, calibs, coord_ranges, _, info) in enumerate(self.data_loader):
            
            # load evaluation data and move data to current device.
            inputs = inputs.to(self.device)
            calibs = calibs.to(self.device)
            coord_ranges = coord_ranges.to(self.device)
            
            # the outputs of centernet
            outputs = self.model(inputs,coord_ranges,calibs,K=50,mode='test')
            dets = extract_dets_from_outputs(outputs=outputs, K=50)
            dets = dets.detach().cpu().numpy()

            # get corresponding calibs & transform tensor to numpy
            for index in info['img_id']:
                calibs = [self.data_loader.dataset.get_calib(index)]
                image_num = index 
           
            image_i_want = inputs.squeeze(0).permute(1,2,0).detach().cpu().numpy()
            image_i_want = image_i_want * np.array([0.229, 0.224, 0.225], dtype=np.float32) + np.array([0.485, 0.456, 0.406], dtype=np.float32)
            image_i_want = cv2.cvtColor(image_i_want*255.0, cv2.COLOR_BGR2RGB)
           
            info = {key: val.detach().cpu().numpy() for key, val in info.items()}
            cls_mean_size = self.data_loader.dataset.cls_mean_size
            dets, img = decode_detections(dets = dets,
                                     info = info,
                                     calibs = calibs,
                                     cls_mean_size=cls_mean_size,
                                     threshold = self.cfg['threshold'],
                                     img = image_i_want)
            
            image_num = '{0:06d}'.format(int(image_num))
            cv2.imwrite('/data/gkstmf616/project/GUPNet/code/result_tester/' +str(image_num)+'.jpg',img)
            
            results.update(dets)
            progress_bar.update()
        
        # save the result for evaluation.
        self.save_results(results)  
        progress_bar.close()
          

    def save_results(self, results, output_dir='./outputs'):
        output_dir = os.path.join(output_dir, 'data')
        os.makedirs(output_dir, exist_ok=True)
        for img_id in results.keys():
            out_path = os.path.join(output_dir, '{:06d}.txt'.format(img_id))
            f = open(out_path, 'w')
            for i in range(len(results[img_id])):
                class_name = self.class_name[int(results[img_id][i][0])]
                f.write('{} 0.0 0'.format(class_name))
                for j in range(1, len(results[img_id][i])):
                    f.write(' {:.2f}'.format(results[img_id][i][j]))
                f.write('\n')
            f.close()
           