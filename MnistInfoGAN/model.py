#!/Users/apple/anaconda2/envs/keras/bin/python
import tensorflow as tf
import ipdb
def batchnormalize(X,eps=1e-8,g=None,b=None):
    if X.get_shape().ndims==4:
        mean=tf.reduce_mean(X,[0,1,2])
        std=tf.reduce_mean(tf.square(X-mean),[0,1,2])
        X=(X-mean)/tf.sqrt(std+eps)

        if g is not None and b is not None:
            g=tf.reshape(g,[1,1,1,-1])
            b=tf.reshape(b,[1,1,1,-1])
            X=X*g+b
    elif X.get_shape().ndims==2:
        mean=tf.reduce_mean(X,0)
        std = tf.reduce_mean(tf.square(X-mean),0)
        X   = (X-mean)/tf.sqrt(std+eps)

        if g is not None and b is not None:
            g=tf.reshape(g,[1,-1])
            b=tf.reshape(b,[1,-1])
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
    return -(t*tf.log(o)+(1.-t)*tf.log(1.-o))

class INFOGAN():
    def __init__(
            self,
            batch_size=100,
            image_shape=[28,28,1],
            dim_z=100,
            dim_s=10,
            dim_W1=1024,
            dim_W2=128,
            dim_W3=64,
            dim_channel=1,
            L=0.01
    ):
        self.batch_size=batch_size
        self.image_shape=image_shape
        self.dim_z=dim_z
        self.dim_y=dim_s;
        self.L=L

        self.dim_W1=dim_W1
        self.dim_W2=dim_W2
        self.dim_W3=dim_W3
        self.dim_channel=dim_channel

        self.gen_W1=tf.Variable(tf.random_normal([dim_z+dim_s,dim_W1],stddev=0.02),name='gen_W1')
        self.gen_W2=tf.Variable(tf.random_normal([dim_W1,dim_W2*7*7],stddev=0.02),name='gen_W2')
        self.gen_W3=tf.Variable(tf.random_normal([5,5,dim_W3,dim_W2],stddev=0.02),name='genW3')
        self.gen_W4=tf.Variable(tf.random_normal([5,5,dim_channel,dim_W3],stddev=0.02),name='gen_W4')

        self.discrim_W1=tf.Variable(tf.random_normal([5,5,dim_channel,dim_W3],stddev=0.02),name='discrim_W1')
        self.discrim_W2=tf.Variable(tf.random_normal([5,5,dim_W3,dim_W2],stddev=0.02),name='discrim_W2')
        self.discrim_W3=tf.Variable(tf.random_normal([dim_W2*7*7,dim_W1],stddev=0.02),name='discrim_W3')
        self.discrim_W4=tf.Variable(tf.random_normal([dim_W1,1],stddev=0.02),name='discrim_W4')
        self.Qyx=tf.Variable(tf.random_normal([dim_W1,dim_s],stddev=0.02),name='gen_Qyx')

    def build_model(self):
        Z=tf.placeholder(tf.float32,[self.batch_size,self.dim_z])
        Y=tf.placeholder(tf.float32,[self.batch_size,self.dim_y])

        image_real=tf.placeholder(tf.float32,[self.batch_size]+self.image_shape)
        image_gen =self.generate(Z,Y)

        _,p_real=self.discriminate(image_real)
        Qyx,p_gen =self.discriminate(image_gen)

        discrim_cost_real=bce(p_real,tf.ones_like(p_real))
        discrim_cost_gen =bce(p_gen,tf.zeros_like(p_gen))

        discrim_cost = tf.reduce_mean(discrim_cost_real)+tf.reduce_mean(discrim_cost_gen)
        gen_cost = tf.reduce_mean(bce(p_gen,tf.ones_like(p_gen)))+self.L*(-1.*tf.reduce_mean(tf.log(Qyx)))

        return Z,Y,image_real,discrim_cost,gen_cost,p_real,p_gen
    def generate(self,Z,Y):
        Z=tf.concat(1,[Z,Y])
        h1=tf.nn.relu(batchnormalize(tf.matmul(Z,self.gen_W1)))
        h2=tf.nn.relu(batchnormalize(tf.matmul(h1,self.gen_W2)))
        h2=tf.reshape(h2,[self.batch_size,7,7,self.dim_W2])

        output_shape_l3=[self.batch_size,14,14,self.dim_W3]
        h3=tf.nn.conv2d_transpose(h2,self.gen_W3,output_shape=output_shape_l3,strides=[1,2,2,1])
        h3=tf.nn.relu(batchnormalize(h3))

        output_shape_l4=[self.batch_size,28,28,self.dim_channel]
        h4=tf.nn.conv2d_transpose(h3,self.gen_W4,output_shape=output_shape_l4,strides=[1,2,2,1])
        x=tf.nn.sigmoid(h4)
        return x
    def discriminate(self,image):

        h1=lrelu(tf.nn.conv2d(image,self.discrim_W1,strides=[1,2,2,1],padding='SAME'))

        h2=lrelu(batchnormalize(tf.nn.conv2d(h1,self.discrim_W2,strides=[1,2,2,1],padding='SAME')))
        h2=tf.reshape(h2,[self.batch_size,-1])

        h3=lrelu(batchnormalize(tf.matmul(h2,self.discrim_W3)))

        h4=tf.nn.sigmoid(batchnormalize(tf.matmul(h3,self.discrim_W4)))
        Qyx=tf.nn.sigmoid(batchnormalize(tf.matmul(h3,self.Qyx)))
        return h4,Qyx
    def samples_generator(self,batch_size):
        Z=tf.placeholder(tf.float32,[batch_size,self.dim_z])
        Y=tf.placeholder(tf.float32,[batch_size,self.dim_y])

        Z_=tf.concat(1,[Y,Z])
        h1=tf.nn.relu(batchnormalize(tf.matmul(Z_,self.gen_W1)))

        h2=tf.nn.relu(batchnormalize(tf.matmul(h1,self.gen_W2)))
        h2=tf.reshape(h2,[batch_size,7,7,self.dim_W2])

        output_shape_l3=[batch_size,14,14,self.dim_W3]
        h3=tf.nn.conv2d_transpose(h2,self.gen_W3,output_shape=output_shape_l3,strides=[1,2,2,1])
        h3=tf.nn.relu(batchnormalize(h3))

        output_shape_l4=[batch_size,28,28,self.dim_channel]
        h4=tf.nn.conv2d_transpose(h3,self.gen_W4,output_shape=output_shape_l4,strides=[1,2,2,1])
        x=tf.nn.sigmoid(h4)
        return Z,Y,x

