-- script for dumping statistics about charCNN weights
-- works best with cudnn (the alternative -temp_conv option doesn't dump all the statistics)
-- Acknowledgement: uses code from https://github.com/harvardnlp/seq2seq-attn

require 'nn'
require 'nngraph'
require 's2sa.data'
require 's2sa.models'
require 'cudnn'



local cmd = torch.CmdLine()

-- file location
cmd:option('-model', 'model.t7.', [[Path to model .t7 file]])
--cmd:option('weightFile', 'weights.txt', [[Path to save char cnn weights]])
cmd:option('-temp_conv', false, [[Model trained with temporal convolution (not cudnn option)]])
opt = cmd:parse(arg)

function get_layer(layer)
  if layer.name ~= nil then
    if layer.name == 'charcnn_enc' then
      charcnn = layer
    end
  end
end


checkpoint = torch.load(opt.model)
model = checkpoint[1]
model[1]:apply(get_layer)
--print(model[1])
--print(charcnn)
if opt.temp_conv then
  weights = charcnn.modules[2]:double()
  print('')
  print('average variance overall: ' .. weights:var(2):mean())
else 
  weights = charcnn.modules[3].weight:double()
  weights = weights:squeeze()
  print('')
  print('average variance overall: ' .. weights:var(2):mean())
  print('average variance per char embedding dim:')
  print(weights:var(2):mean(1):squeeze())
  print('variance of variances: ' .. weights:var(2):var())
end
 





