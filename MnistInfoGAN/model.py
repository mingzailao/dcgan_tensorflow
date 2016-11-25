import tensorflow as tf
import ipdb

def batchnormalize(X,eps=1e-8,g=None,b=None):
    if X.get_shape().ndims=4:
        mean=tf.reduce_mean(X,[0,1,2])
        std=tf.reduce_mean(tf.square(X-mean),[0,1,2])
        X=(X-mean)/(tf.sqrt(std+eps))
        if g is not None and b is not None:
            g=tf.reshape(g,[1,1,1,-1])
            b=tf.reshape(b,[1,1,1,-1])
            X=X*g+b

    elif X.get_shape().ndims=2:
        mean=tf.reduce_mean(X,0)
        std =tf.reduce_mean(tf.square(X-mean),0)
        X=(X-mean)/(tf.sqrt(std+eps))
        if g is not None and b is not None:
            X=X*g+b
    else:
        raise NotImplementedError
    return X
def lrelu(X,leak=0.2):
    f1=0.5*(1+leak)
    f2=0.5*(1-leak)
    return f1*X+f2*tf.abs(X)

def bce(o,t):
    o=tf.clip_by_value(o,1e-7,1.-1e-7)
    return -(t*tf.log(o)+(1.-t)*(tf.log(1.-o)))

class INFOGAN():
    def _init_(
            self,
            batch_size=100,
            image_shape=[28,28,1],
            dim_z=100,
            dim_s=10,
            dim_W1=1024,
            dim_W2=128,
            dim_W3=64,
            dim_channel=1,
    ):
        self.batch_size=batch_size
        self.image_shape=image_shape
        self.dim_z=dim_z
        self.dim_s=dims

        self.dim_W1=dim_W1,
        self.dim_W2=dim_W2,
        self.dim_W3=dim_W3,
        self.dim_channel=dim_channel

        self.gen_W1=tf.Variable()
        self.gen_W2=tf.Variable()
        self.gen_W3=tf.Variable()
        self.gen_W4=tf.Variable()

        self.discrim_W1=tf.Variable()
        self.discrim_W2=tf.Variable()
        self.discrim_W3=tf.Variable()
        self.discrim_W4=tf.Variable()
