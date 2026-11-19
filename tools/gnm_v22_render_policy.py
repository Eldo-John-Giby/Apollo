"""Apply deterministic judging settings without changing the saved source scene."""


def apply(scene,samples=None):
    if samples is not None:
        if type(samples) is not int or samples<=0:raise ValueError('Samples must be a positive integer')
        scene.cycles.samples=samples
    scene.render.engine='CYCLES';scene.cycles.device='CPU'
    scene.cycles.seed=20261119;scene.cycles.use_animated_seed=False
    scene.cycles.use_adaptive_sampling=False;scene.cycles.time_limit=0
    scene.cycles.use_denoising=True
    scene.render.use_motion_blur=False;scene.render.dither_intensity=0
    scene.camera.data.dof.use_dof=False
    disabled=[]
    if scene.use_nodes and scene.node_tree:
        for node in scene.node_tree.nodes:
            if node.type!='MIX_RGB' or not node.inputs[2].is_linked:continue
            source=node.inputs[2].links[0].from_node
            if source.type=='TEXTURE' and source.texture and source.texture.type=='NOISE':
                if node.inputs[0].is_linked:
                    raise ValueError('Animated or linked grain factor requires explicit handling')
                node.inputs[0].default_value=0
                disabled.append(node.name)
    return dict(device='CPU',seed=20261119,adaptive_sampling=False,time_limit=0,
                animated_seed=False,denoising=True,motion_blur=False,
                dither_intensity=0,depth_of_field=False,disabled_random_grain_nodes=sorted(disabled))
