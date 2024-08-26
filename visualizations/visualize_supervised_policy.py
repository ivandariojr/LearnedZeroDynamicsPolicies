import jax.random
from train import wandb_model_load
from hydra.utils import instantiate
import wandb
import jax
import matplotlib.pyplot as plt
import numpy as np
import jax.numpy as jnp
import tf2onnx
import onnx
from utils import tfZeroInvariantMLP


plt.rc('font', family='serif')

'''Visualizes the Policy, and a sample trajectory'''


def main():
    exp_name = 'wdc3iii/zero_dynamics_policies/sffry2cb'
    # exp_name = 'wdc3iii/zero_dynamics_policies/r9erc0lx'
    model_tag = os.path.basename(exp_name)

    model_name = f'{exp_name}_model:best'
    api = wandb.Api()
    cfg, state = wandb_model_load(api, model_name)

    new_rng, split = jax.random.split(state.rng)
    state = state.replace(rng=new_rng)

    # Instantiate the Policy
    integrator = instantiate(cfg.loss.integrator)

    state_n = 4
    policy = integrator.mlp
    params = policy.init(split, jnp.zeros((state_n,)))

    params['params'] = state.params['mlp']['params']

    # Sample the policy

    # setup rng
    rng = jax.random.PRNGKey(cfg.seed)
    rng, split = jax.random.split(rng)
    dataset = instantiate(cfg.dataset)(rng=split)
    zs = dataset.x_values
    plt.figure()
    ax = plt.subplot(121)
    # im = plot_2D_irregular_heatmap(zs[:, 0], zs[:, 2], eta_d[:, 0],ax=ax)
    # plot_scatter_value(zs[:, 1], zs[:, 3], dataset.y_values[:, 0])
    ax.scatter(zs[:, 0], zs[:, 2], c=dataset.y_values[:, 0], s=10)
    # plt.colorbar(im, ax=ax)
    plt.xlabel('x')
    plt.ylabel('dotx')
    plt.title('theta1_dataset')
    ax = plt.subplot(122)
    # im = plot_2D_irregular_heatmap(zs[:, 1], zs[:, 3], eta_d[:, 1],ax=ax)
    # plot_scatter_value(zs[:, 1], zs[:, 3], dataset.y_values[:, 1])
    ax.scatter(zs[:, 1], zs[:, 3], c=dataset.y_values[:, 1], s=10)
    # plt.colorbar(im, ax=ax)
    plt.xlabel('y')
    plt.ylabel('doty')
    plt.title('theta2_dataset')
    plt.show()


    eta_d = jax.vmap(policy.apply, in_axes=(None, 0))(params, zs)

    # new_rng, split = jax.random.split(new_rng)

    # Plot
    plt.figure()
    ax = plt.subplot(121)
    # plot_scatter_value(zs[:, 0], zs[:, 2], eta_d[:, 0] - dataset.y_values[:,0])
    im = ax.scatter(zs[:, 0], zs[:, 2], c=eta_d[:, 0] - dataset.y_values[:,0],s=1)
    # plt.colorbar(im, ax=ax)
    plt.xlabel('x')
    plt.ylabel('dotx')
    plt.title('theta1_d error')
    ax = plt.subplot(122)
    # plot_scatter_value(zs[:, 1], zs[:, 3], eta_d[:, 1] - dataset.y_values[:, 1])
    ax.scatter(zs[:, 1], zs[:, 3], c=eta_d[:, 1] - dataset.y_values[:,1],s=1)
    # plt.colorbar(im, ax=ax)
    plt.xlabel('y')
    plt.ylabel('doty')
    plt.title('theta2_d error')
    plt.show()

    zs = jax.random.uniform(split, shape=(10000, 4), minval=-1, maxval=1)
    zs = zs * jnp.array([[0.5, 0.5, 0.2, 0.2]])
    eta_d = jax.vmap(policy.apply, in_axes=(None, 0))(params, zs)
    plt.figure()
    ax = plt.subplot(121)
    # im = plot_2D_irregular_heatmap(zs[:, 0], zs[:, 2], eta_d[:, 0],ax=ax)
    # plot_scatter_value(zs[:, 0], zs[:, 2], eta_d[:, 0])
    ax.scatter(zs[:, 0], zs[:, 2], c=eta_d[:, 0], s=10)
    # plt.colorbar(im, ax=ax)
    plt.xlabel('x')
    plt.ylabel('dotx')
    plt.title('theta1_d')
    ax = plt.subplot(122)
    # im = plot_2D_irregular_heatmap(zs[:, 1], zs[:, 3], eta_d[:, 1],ax=ax)
    # plot_scatter_value(zs[:, 1], zs[:, 3], eta_d[:, 1])
    ax.scatter(zs[:, 1], zs[:, 3], c=eta_d[:, 1], s=10)
    # plt.colorbar(im, ax=ax)
    plt.xlabel('y')
    plt.ylabel('doty')
    plt.title('theta2_d')
    plt.show()

    single_sample_input = jnp.linspace(-1, 1, num=1000)
    single_sample_input = jnp.reshape(single_sample_input, (-1, 1))
    z = jnp.zeros((1000, 1))

    plt.figure()
    ax = plt.subplot(121)
    input = jnp.concatenate([single_sample_input, z,z,z],axis=1)
    eta_d = jax.vmap(policy.apply, in_axes=(None, 0))(params, input)
    ax.scatter(input[:, 0], eta_d[:,0], color='b')
    ax = plt.subplot(122)
    ax.scatter(input[:, 0], eta_d[:, 1], color='b')
    plt.show()

    plt.figure()
    ax = plt.subplot(121)
    input = jnp.concatenate([z,single_sample_input,z,z],axis=1)
    eta_d = jax.vmap(policy.apply, in_axes=(None, 0))(params, input)
    ax.scatter(input[:, 1], eta_d[:, 0], color='b')
    ax = plt.subplot(122)
    ax.scatter(input[:, 1], eta_d[:, 1], color='b')
    plt.show()

    plt.figure()
    ax = plt.subplot(121)
    input = jnp.concatenate([z, z, single_sample_input, z],axis=1)
    eta_d = jax.vmap(policy.apply, in_axes=(None, 0))(params, input)
    ax.scatter(input[:, 2], eta_d[:, 0], color='b')
    ax = plt.subplot(122)
    ax.scatter(input[:, 2], eta_d[:, 1], color='b')
    plt.show()

    plt.figure()
    ax = plt.subplot(121)
    input = jnp.concatenate([z, z, z, single_sample_input],axis=1)
    eta_d = jax.vmap(policy.apply, in_axes=(None, 0))(params, input)
    ax.scatter(input[:, 3], eta_d[:, 0], color='b')
    ax = plt.subplot(122)
    ax.scatter(input[:, 3], eta_d[:, 1], color='b')
    plt.show()

    tf_model = tfZeroInvariantMLP(policy.mlp, params['params']['mlp'], state_n, cfg.loss.integrator.mlp.mlp.activation._target_)

    # Validate tf_model vs flax model
    zs = jax.random.uniform(split, shape=(10000, 4), minval=-1, maxval=1)
    eta_d_flax = jax.vmap(policy.apply, in_axes=(None, 0))(params, zs)

    eta_d_tf = tf_model(np.array(zs))
    err = eta_d_flax - eta_d_tf
    print(np.max(np.abs(np.array(err))))

    onnx_model = tf2onnx.convert.from_keras(tf_model)
    onnx.save(onnx_model[0], os.getcwd()+f'/../models/trained_model_{model_tag}.onnx')

    print("success!")


if __name__ == "__main__":
    import os
    os.environ["XLA_PYTHON_CLIENT_ALLOCATOR"] = "platform"
    os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"
    os.environ["JAX_ENABLE_X64"] = "true"
    from jax import config

    config.update("jax_enable_x64", True)
    from jax.experimental.compilation_cache import compilation_cache as cc

    cc.initialize_cache("/tmp/jax_cache")

    main()
