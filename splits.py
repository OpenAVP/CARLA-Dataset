# from typing import Dict, List

# train_detect = \
#     ['v1.0-demo', 'v1.0-demo_1', 'v1.0-demo_2', 'v1.0-demo_3', 'v1.0-demo_4', 'v1.0-demo_5',
#     'v1.0-demo_6', 'v1.0-demo_7', 'v1.0-demo_8', 'v1.0-demo_9', 'v1.0-demo_10', 'v1.0-demo_11',
#     'v1.0-demo_12', 'v1.0-demo_13', 'v1.0-demo_14', 'v1.0-demo_15', 'v1.0-demo_16', 'v1.0-demo_17',
#     'v1.0-demo_18', 'v1.0-demo_19', 'v1.0-demo_20', 'v1.0-demo_21', 'v1.0-demo_22', 'v1.0-demo_23',
#     'v1.0-demo_24', 'v1.0-demo_25', 'v1.0-demo_26', 'v1.0-demo_27', 'v1.0-demo_28', 'v1.0-demo_29',
#     'v1.0-demo_30', 'v1.0-demo_31']

# train_track = \
#     ['v1.0-demo_32', 'v1.0-demo_33', 'v1.0-demo_34', 'v1.0-demo_35', 'v1.0-demo_36', 'v1.0-demo_37',
#     'v1.0-demo_38', 'v1.0-demo_39', 'v1.0-demo_40', 'v1.0-demo_41', 'v1.0-demo_42', 'v1.0-demo_43',
#     'v1.0-demo_44', 'v1.0-demo_45', 'v1.0-demo_46', 'v1.0-demo_47', 'v1.0-demo_48', 'v1.0-demo_49',
#     'v1.0-demo_50', 'v1.0-demo_51', 'v1.0-demo_52', 'v1.0-demo_53', 'v1.0-demo_54', 'v1.0-demo_55',
#     'v1.0-demo_56', 'v1.0-demo_57', 'v1.0-demo_58', 'v1.0-demo_59', 'v1.0-demo_60', 'v1.0-demo_61',
#     'v1.0-demo_62', 'v1.0-demo_63']

# train = list(sorted(set(train_detect + train_track)))

# val = \
#     ['v1.0-demo_64', 'v1.0-demo_65', 'v1.0-demo_66', 'v1.0-demo_67', 'v1.0-demo_68', 'v1.0-demo_69',
#     'v1.0-demo_70', 'v1.0-demo_71', 'v1.0-demo_72', 'v1.0-demo_73', 'v1.0-demo_74', 'v1.0-demo_75',
#     'v1.0-demo_76']
    
# trainval = list(sorted(set(train + val)))

# test = \
#     ['v1.0-demo_77', 'v1.0-demo_78', 'v1.0-demo_79', 'v1.0-demo_80', 'v1.0-demo_81', 'v1.0-demo_82',
#     'v1.0-demo_83', 'v1.0-demo_84', 'v1.0-demo_85', 'v1.0-demo_86', 'v1.0-demo_87', 'v1.0-demo_88',
#     'v1.0-demo_89']

# mini_train = \
#     ['v1.0-demo_1', 'v1.0-demo_20', 'v1.0-demo_27', 'v1.0-demo_35', 'v1.0-demo_36', 'v1.0-demo_49', 'v1.0-demo_60', 'v1.0-demo_73']

# mini_val = \
#     ['v1.0-demo_65', 'v1.0-demo_75']
    
# mini = list(sorted(set(mini_train + mini_val)))

####################################################################################################################################

# train_detect = \
#     ['v1.0-demo', 'v1.0-demo_1', 'v1.0-demo_2', 'v1.0-demo_3', 'v1.0-demo_4', 'v1.0-demo_5',
#     'v1.0-demo_6', 'v1.0-demo_7', 'v1.0-demo_8', 'v1.0-demo_9', 'v1.0-demo_10', 'v1.0-demo_11',
#     'v1.0-demo_12', 'v1.0-demo_13', 'v1.0-demo_14', 'v1.0-demo_15', 'v1.0-demo_16', 'v1.0-demo_17',
#     'v1.0-demo_18', 'v1.0-demo_19', 'v1.0-demo_20', 'v1.0-demo_21', 'v1.0-demo_22', 'v1.0-demo_23',
#     'v1.0-demo_24', 'v1.0-demo_25', 'v1.0-demo_26', 'v1.0-demo_27', 'v1.0-demo_28', 'v1.0-demo_29',
#     'v1.0-demo_30', 'v1.0-demo_31','v1.0-demo_90','v1.0-demo_91','v1.0-demo_92','v1.0-demo_93',
#     'v1.0-demo_94','v1.0-demo_95','v1.0-demo_96','v1.0-demo_97','v1.0-demo_98','v1.0-demo_99',
#     'v1.0-demo_100','v1.0-demo_101','v1.0-demo_102','v1.0-demo_103','v1.0-demo_104','v1.0-demo_105',
#     'v1.0-demo_122','v1.0-demo_123','v1.0-demo_124','v1.0-demo_125','v1.0-demo_126','v1.0-demo_127',
#     'v1.0-demo_134','v1.0-demo_135','v1.0-demo_136','v1.0-demo_137','v1.0-demo_138','v1.0-demo_139',
#     'v1.0-demo_156','v1.0-demo_157','v1.0-demo_158','v1.0-demo_159','v1.0-demo_160','v1.0-demo_161',
#     'v1.0-demo_162','v1.0-demo_163','v1.0-demo_164','v1.0-demo_165','v1.0-demo_166','v1.0-demo_167',
#     'v1.0-demo_168','v1.0-demo_169','v1.0-demo_170','v1.0-demo_171','v1.0-demo_172','v1.0-demo_173',
#     'v1.0-demo_204','v1.0-demo_205','v1.0-demo_206','v1.0-demo_207','v1.0-demo_208','v1.0-demo_209',
#     'v1.0-demo_210','v1.0-demo_211','v1.0-demo_212','v1.0-demo_213','v1.0-demo_214','v1.0-demo_215',
#     'v1.0-demo_216','v1.0-demo_217','v1.0-demo_218','v1.0-demo_219','v1.0-demo_220','v1.0-demo_221',
#     'v1.0-demo_252','v1.0-demo_253','v1.0-demo_254','v1.0-demo_255','v1.0-demo_256','v1.0-demo_257',
#     'v1.0-demo_258','v1.0-demo_259','v1.0-demo_260','v1.0-demo_261','v1.0-demo_262','v1.0-demo_263',
#     'v1.0-demo_264','v1.0-demo_265','v1.0-demo_266','v1.0-demo_357','v1.0-demo_358','v1.0-demo_269',
#     'v1.0-demo_300','v1.0-demo_301','v1.0-demo_302','v1.0-demo_303','v1.0-demo_304','v1.0-demo_305',
#     'v1.0-demo_312','v1.0-demo_313','v1.0-demo_314','v1.0-demo_315','v1.0-demo_316','v1.0-demo_317',
#     'v1.0-demo_318','v1.0-demo_319','v1.0-demo_320','v1.0-demo_321','v1.0-demo_322','v1.0-demo_323',
#     'v1.0-demo_348','v1.0-demo_349','v1.0-demo_350','v1.0-demo_354','v1.0-demo_355']

# train_track = \
#     ['v1.0-demo_32', 'v1.0-demo_33', 'v1.0-demo_34', 'v1.0-demo_35', 'v1.0-demo_36', 'v1.0-demo_37',
#     'v1.0-demo_38', 'v1.0-demo_39', 'v1.0-demo_40', 'v1.0-demo_41', 'v1.0-demo_42', 'v1.0-demo_43',
#     'v1.0-demo_44', 'v1.0-demo_45', 'v1.0-demo_46', 'v1.0-demo_47', 'v1.0-demo_48', 'v1.0-demo_49',
#     'v1.0-demo_50', 'v1.0-demo_51', 'v1.0-demo_52', 'v1.0-demo_53', 'v1.0-demo_54', 'v1.0-demo_55',
#     'v1.0-demo_56', 'v1.0-demo_57', 'v1.0-demo_58', 'v1.0-demo_59', 'v1.0-demo_60', 'v1.0-demo_61',
#     'v1.0-demo_62', 'v1.0-demo_63','v1.0-demo_106','v1.0-demo_107','v1.0-demo_108','v1.0-demo_109',
#     'v1.0-demo_110','v1.0-demo_111','v1.0-demo_112','v1.0-demo_113','v1.0-demo_114','v1.0-demo_115',
#     'v1.0-demo_116','v1.0-demo_117','v1.0-demo_118','v1.0-demo_119','v1.0-demo_120','v1.0-demo_121',
#     'v1.0-demo_128','v1.0-demo_129','v1.0-demo_130','v1.0-demo_131','v1.0-demo_132','v1.0-demo_133',
#     'v1.0-demo_140','v1.0-demo_141','v1.0-demo_142','v1.0-demo_143','v1.0-demo_144','v1.0-demo_145',
#     'v1.0-demo_174','v1.0-demo_175','v1.0-demo_176','v1.0-demo_177','v1.0-demo_178','v1.0-demo_179',
#     'v1.0-demo_180','v1.0-demo_181','v1.0-demo_182','v1.0-demo_183','v1.0-demo_184','v1.0-demo_185',
#     'v1.0-demo_186','v1.0-demo_187','v1.0-demo_188','v1.0-demo_189','v1.0-demo_190','v1.0-demo_191',
#     'v1.0-demo_222','v1.0-demo_223','v1.0-demo_224','v1.0-demo_225','v1.0-demo_226','v1.0-demo_227',
#     'v1.0-demo_228','v1.0-demo_229','v1.0-demo_230','v1.0-demo_231','v1.0-demo_232','v1.0-demo_233',
#     'v1.0-demo_234','v1.0-demo_235','v1.0-demo_236','v1.0-demo_237','v1.0-demo_238','v1.0-demo_239',
#     'v1.0-demo_270','v1.0-demo_271','v1.0-demo_272','v1.0-demo_273','v1.0-demo_274','v1.0-demo_275',
#     'v1.0-demo_276','v1.0-demo_277','v1.0-demo_278','v1.0-demo_279','v1.0-demo_280','v1.0-demo_281',
#     'v1.0-demo_282','v1.0-demo_283','v1.0-demo_284','v1.0-demo_285','v1.0-demo_286','v1.0-demo_287',
#     'v1.0-demo_306','v1.0-demo_307','v1.0-demo_308','v1.0-demo_309','v1.0-demo_310','v1.0-demo_311',
#     'v1.0-demo_324','v1.0-demo_325','v1.0-demo_326','v1.0-demo_327','v1.0-demo_328','v1.0-demo_329',
#     'v1.0-demo_330','v1.0-demo_331','v1.0-demo_332','v1.0-demo_333','v1.0-demo_334','v1.0-demo_335',
#     'v1.0-demo_351','v1.0-demo_352','v1.0-demo_353','v1.0-demo_356']

# train = list(sorted(set(train_detect + train_track)))

# val = \
#     ['v1.0-demo_64', 'v1.0-demo_65', 'v1.0-demo_66', 'v1.0-demo_67', 'v1.0-demo_68', 'v1.0-demo_69',
#     'v1.0-demo_70', 'v1.0-demo_71', 'v1.0-demo_72', 'v1.0-demo_73', 'v1.0-demo_74', 'v1.0-demo_75',
#     'v1.0-demo_76','v1.0-demo_146','v1.0-demo_147','v1.0-demo_148','v1.0-demo_149','v1.0-demo_150',
#     'v1.0-demo_192','v1.0-demo_193','v1.0-demo_194','v1.0-demo_195','v1.0-demo_196','v1.0-demo_197',
#     'v1.0-demo_240','v1.0-demo_241','v1.0-demo_242','v1.0-demo_243','v1.0-demo_244','v1.0-demo_245',
#     'v1.0-demo_288','v1.0-demo_289','v1.0-demo_290','v1.0-demo_291','v1.0-demo_292','v1.0-demo_293',
#     'v1.0-demo_336','v1.0-demo_337','v1.0-demo_338','v1.0-demo_339','v1.0-demo_340','v1.0-demo_341',]
    
# trainval = list(sorted(set(train + val)))

# test = \
#     ['v1.0-demo_77', 'v1.0-demo_78', 'v1.0-demo_79', 'v1.0-demo_80', 'v1.0-demo_81', 'v1.0-demo_82',
#     'v1.0-demo_83', 'v1.0-demo_84', 'v1.0-demo_85', 'v1.0-demo_86', 'v1.0-demo_87', 'v1.0-demo_88',
#     'v1.0-demo_89','v1.0-demo_151','v1.0-demo_152','v1.0-demo_153','v1.0-demo_154','v1.0-demo_155',
#     'v1.0-demo_198','v1.0-demo_199','v1.0-demo_200','v1.0-demo_201','v1.0-demo_202','v1.0-demo_203',
#     'v1.0-demo_246','v1.0-demo_247','v1.0-demo_248','v1.0-demo_249','v1.0-demo_250','v1.0-demo_251',
#     'v1.0-demo_294','v1.0-demo_295','v1.0-demo_296','v1.0-demo_297','v1.0-demo_298','v1.0-demo_299',
#     'v1.0-demo_342','v1.0-demo_343','v1.0-demo_344','v1.0-demo_345','v1.0-demo_346','v1.0-demo_347',]

# mini_train = \
#     ['v1.0-demo_1', 'v1.0-demo_20', 'v1.0-demo_27', 'v1.0-demo_35', 'v1.0-demo_36', 'v1.0-demo_49', 
#     'v1.0-demo_60', 'v1.0-demo_73','v1.0-demo_212','v1.0-demo_213','v1.0-demo_274','v1.0-demo_275',
#     'v1.0-demo_321','v1.0-demo_330']

# mini_val = \
#     ['v1.0-demo_65', 'v1.0-demo_75', 'v1.0-demo_242', 'v1.0-demo_293']

# mini = list(sorted(set(mini_train + mini_val)))



#######################################################################################################

train_detect = \
    ['v1.0-demo', 'v1.0-demo_1', 'v1.0-demo_2', 'v1.0-demo_3', 'v1.0-demo_4', 'v1.0-demo_5',
    'v1.0-demo_6', 'v1.0-demo_7', 'v1.0-demo_8', 'v1.0-demo_9', 'v1.0-demo_10', 'v1.0-demo_11',
    'v1.0-demo_12', 'v1.0-demo_13', 'v1.0-demo_14', 'v1.0-demo_15', 'v1.0-demo_16', 'v1.0-demo_17',
    'v1.0-demo_18', 'v1.0-demo_19', 'v1.0-demo_20', 'v1.0-demo_21', 'v1.0-demo_22', 'v1.0-demo_23',
    'v1.0-demo_24', 'v1.0-demo_25', 'v1.0-demo_26', 'v1.0-demo_27', 'v1.0-demo_28', 'v1.0-demo_29',
    'v1.0-demo_30', 'v1.0-demo_31','v1.0-demo_90','v1.0-demo_91','v1.0-demo_92','v1.0-demo_93',
    'v1.0-demo_94','v1.0-demo_95','v1.0-demo_96','v1.0-demo_97','v1.0-demo_98','v1.0-demo_99',
    'v1.0-demo_100','v1.0-demo_101','v1.0-demo_102','v1.0-demo_103','v1.0-demo_104','v1.0-demo_105',
    'v1.0-demo_122','v1.0-demo_123','v1.0-demo_124','v1.0-demo_125','v1.0-demo_126','v1.0-demo_127',
    'v1.0-demo_134','v1.0-demo_135','v1.0-demo_136','v1.0-demo_137','v1.0-demo_138','v1.0-demo_139',
    'v1.0-demo_156','v1.0-demo_157','v1.0-demo_158','v1.0-demo_164','v1.0-demo_165','v1.0-demo_166',
    'v1.0-demo_174','v1.0-demo_175','v1.0-demo_176','v1.0-demo_177','v1.0-demo_178','v1.0-demo_184',
    'v1.0-demo_186','v1.0-demo_187','v1.0-demo_188']

train_track = \
    ['v1.0-demo_32', 'v1.0-demo_33', 'v1.0-demo_34', 'v1.0-demo_35', 'v1.0-demo_36', 'v1.0-demo_37',
    'v1.0-demo_38', 'v1.0-demo_39', 'v1.0-demo_40', 'v1.0-demo_41', 'v1.0-demo_42', 'v1.0-demo_43',
    'v1.0-demo_44', 'v1.0-demo_45', 'v1.0-demo_46', 'v1.0-demo_47', 'v1.0-demo_48', 'v1.0-demo_49',
    'v1.0-demo_50', 'v1.0-demo_51', 'v1.0-demo_52', 'v1.0-demo_53', 'v1.0-demo_54', 'v1.0-demo_55',
    'v1.0-demo_56', 'v1.0-demo_57', 'v1.0-demo_58', 'v1.0-demo_59', 'v1.0-demo_60', 'v1.0-demo_61',
    'v1.0-demo_62', 'v1.0-demo_63','v1.0-demo_106','v1.0-demo_107','v1.0-demo_108','v1.0-demo_109',
    'v1.0-demo_110','v1.0-demo_111','v1.0-demo_112','v1.0-demo_113','v1.0-demo_114','v1.0-demo_115',
    'v1.0-demo_116','v1.0-demo_117','v1.0-demo_118','v1.0-demo_119','v1.0-demo_120','v1.0-demo_121',
    'v1.0-demo_128','v1.0-demo_129','v1.0-demo_130','v1.0-demo_131','v1.0-demo_132','v1.0-demo_133',
    'v1.0-demo_140','v1.0-demo_141','v1.0-demo_142','v1.0-demo_143','v1.0-demo_144','v1.0-demo_145',
    'v1.0-demo_159','v1.0-demo_160','v1.0-demo_161','v1.0-demo_162','v1.0-demo_163','v1.0-demo_167',
    'v1.0-demo_179','v1.0-demo_180','v1.0-demo_181','v1.0-demo_182','v1.0-demo_183','v1.0-demo_185',
    'v1.0-demo_189','v1.0-demo_190','v1.0-demo_191']

train = list(sorted(set(train_detect + train_track)))

val = \
    ['v1.0-demo_64', 'v1.0-demo_65', 'v1.0-demo_66', 'v1.0-demo_67', 'v1.0-demo_68', 'v1.0-demo_69',
    'v1.0-demo_70', 'v1.0-demo_71', 'v1.0-demo_72', 'v1.0-demo_73', 'v1.0-demo_74', 'v1.0-demo_75',
    'v1.0-demo_76','v1.0-demo_146','v1.0-demo_147','v1.0-demo_148','v1.0-demo_149','v1.0-demo_150',
    'v1.0-demo_168','v1.0-demo_169','v1.0-demo_170']
    
trainval = list(sorted(set(train + val)))

test = \
    ['v1.0-demo_77', 'v1.0-demo_78', 'v1.0-demo_79', 'v1.0-demo_80', 'v1.0-demo_81', 'v1.0-demo_82',
    'v1.0-demo_83', 'v1.0-demo_84', 'v1.0-demo_85', 'v1.0-demo_86', 'v1.0-demo_87', 'v1.0-demo_88',
    'v1.0-demo_89','v1.0-demo_151','v1.0-demo_152','v1.0-demo_153','v1.0-demo_154','v1.0-demo_155',
    'v1.0-demo_171','v1.0-demo_172','v1.0-demo_173']

mini_train = \
    ['v1.0-demo_1', 'v1.0-demo_20', 'v1.0-demo_27', 'v1.0-demo_35', 'v1.0-demo_136', 'v1.0-demo_145', 
    'v1.0-demo_160','v1.0-demo_166','v1.0-demo_167','v1.0-demo_177','v1.0-demo_182']

mini_val = \
    ['v1.0-demo_65', 'v1.0-demo_75', 'v1.0-demo_146','v1.0-demo_170']

mini = list(sorted(set(mini_train + mini_val)))
