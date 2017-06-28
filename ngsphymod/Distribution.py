#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse,csv,datetime,logging,os,subprocess,sys,threading,time
import numpy as np
import random as rnd
from scipy.stats import  binom,expon,gamma,lognorm,norm,nbinom,poisson,uniform


class NGSPhyDistribution:

    __relationNumParams=dict({\
        "b":2,#mean,percentages\
        "e":1,#mean\
        "f":1,\
        "g":2,\
        "ln":2,\
        "n":2,\
        "nb":2,\
        "p":1,\
        "r":1,\
        "u":1\
    })
    __DISTRIBUTIONS=__relationNumParams.keys()
    __value=0
    __params=[]
    __distro=""
    __type=None
    __upperLevelDistribution=None

    def __init__(self,type,distroline,upperLevelDistribution):
        self.__type=type
        distroline=distroline.split(":")
        self.__upperLevelDistribution=upperLevelDistribution
        # i depend on another level value
        if (self.__upperLevelDistribution!=None):
            # Value is empty
            if (len(distroline)==1):
                # only have distribution name, meaning
                # distribution has only 1 param and it comes
                # from the upperLevelDistribution
                self.__distro=distroline[0].lower()
            if (len(distroline)==2):
                # i have name and a parameter,
                # meaning, first para comes from above
                # second is the second parameter of my distro
                self.__distro=distroline[0].lower()
                value=self.__upperLevelDistribution.value(1)[0]
                if (self.__distro=="nb" and self.__upperLevelDistribution!=None):
                    self.__params=[value,value]
                else:
                    self.__params=[value,\
                        float(distroline[1].split(",")[0])]
        else:
            self.__distro=distroline[0].lower()
            self.__params=distroline[1].split(",") or []
        if flag:
            self.coverageDistroCheck()

    def setValue(self,value):
        self.__value=value

    def setParams(self,params):
        self.__params=params

    def params(self):
        return self.__params

    def printParams(self):
        print(self.__params)

    def binom(self,samples):
        #n=number of times tested
        #p=probability
        print self.__params
        n=self.__params[0]
        p=self.__params[1]
        distro=binom(n,p)
        f=distro.rvs(size=samples)
        self.__value=f
        return self.__value

    def exponential(self,samples):
        f=np.random.exponential(float(self.__params[0]),size=samples)
        self.__value=f
        return self.__value

    def fixed(self,samples):
        self.__value=[self.__params[0]]*samples
        return self.__value

    def gamma(self,samples):
        # The parameterization with alpha and beta is more common in Bayesian statistics,
        # where the gamma distribution is used as a conjugate prior distribution
        # for various types of inverse scale (aka rate) parameters, such as the
        #lambda of an exponential distribution or a Poisson distribution[4]  or for
        #t hat matter, the beta of the gamma distribution itself.
        #(The closely related inverse gamma distribution is used as a conjugate
        # prior for scale parameters, such as the variance of a normal distribution.)
        # shape, scale = 2., 2. # mean=4, std=2*sqrt(2)
        # s = np.random.gamma(shape, scale, 1000)
        shape=float(self.__params[0]*1.0)
        beta=float(1/self.__params[1]*1.0)
        distro=gamma(shape,beta)
        f=distro.rvs(size=samples)
        self.__value=f
        return self.__value

    def lognorm(self,samples):
        # m=mean, s=sigma - standard deviation
        mean=float(self.__params[0]*1.0)
        sigma=float(self.__params[1]*1.0)
        distro=lognorm(mean,sigma)
        f=distro.rvs(size=samples)
        self.__value=f
        return self.__value

    def nbinom(self,samples):
        # mu= poissonon mean
        # r controls the deviation from the poisson
        # This makes the negative binomial distribution suitable as a robust alternative to the Poisson,
        # which approaches the Poisson for large r, but which has larger variance than the Poisson for small r.
        mu=float(self.__params[0])
        r=float(self.__params[1])
        p=(r*1.0)/(r+mu)
        distro=nbinom(r,p)
        f=distro.rvs(size=samples)
        self.__value=f
        return self.__value

    def normal(self,samples):
        # mean (location) - variance (squared scale)
        locMean=float(self.__params[0]*1.0)
        scaleVariance=float(self.__params[1]*1.0)
        distro=norm(loc=locMean,scale=scaleVariance)
        f=distro.rvs(size=samples)
        self.__value=f
        return self.__value

    def poisson(self,samples):
        l=float(self.__params[0]*1.0)
        distro=poisson(l)
        f=distro.rvs(size=samples)
        self.__value=f
        return self.__value

    def random(self,samples):
        f=np.random.sample(samples)*float(self.__params[0])
        self.__value=f
        return self.__value

    def uniform(self,samples):
        # mean
        mean=float(self.params[0]*1.0)
        distro=uniform(mean)
        f=distro.rvs(size=samples)
        self.__value=f
        return self.__value


    def coverageDistroCheck(self):
        messageOk="{0} Coverage distribution parsing OK. ".format(self.ditroType())
        distroOk=False
        if self.__distro in self.__DISTRIBUTIONS:
            distroOk=True
            # check cas distro - numparameters
            if (self.__relationNumParams[self.__distro]==len(self.__params)):
                # check parameters are numbers
                for index in range(0,len(self.__params)):
                    try:
                        self.__params[index]=float(self.__params[index])
                    except ValueError:
                        messageOk="Not a correct parameter value. Please verify. Exiting"
                        distroOk=False
                        break
            else:
                messageOk="Not the correct number of parameters for the selected distribution. Please verify. Exiting"
                distroOk=False
        else:
            messageOk="Distribution selected is not correct or unavailable. Please verify. Exiting"
        return distroOk, messageOk

    def ditroType(self):
        d=""
        if self.__type==0:
            d="Experiment-level"
        elif self.__type==1:
            d="Individual-level"
        else:
            d="Locus-level"
        return d

    def updateValue(self,value):
        self.__params[0]=value

    def value(self,samples=1):
        try:
            for item in self.__params:
                if item==0:
                    break
            if item==0:
                self.__value=[0]*samples
            else:
                if self.__distro=="b":
                    self.binom(samples)
                if self.__distro=="e":
                    self.exponential(samples)
                if self.__distro=="f":
                    self.fixed(samples)
                if self.__distro=="g":
                    self.gamma(samples)
                if self.__distro=="ln":
                    self.lognormal(samples)
                if self.__distro=="n":
                    self.normal(samples)
                if self.__distro=="nb":
                    self.nbinom(samples)
                if self.__distro=="p":
                    self.poisson(samples)
                if self.__distro=="u":
                    self.uniform(samples)
        except Exception as ex:
            print "OOOOPS!: \t",ex
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit()
        return self.__value

    def distroDescription(self):
        d=""
        if self.__distro=="b":
            d="binom"
        elif self.__distro=="e":
            d="exponential"
        elif self.__distro=="f":
            d="fixed value"
        elif self.__distro=="g":
            d="gamma"
        elif self.__distro=="ln":
            d="lognormal"
        elif self.__distro=="n":
            d="normal"
        elif self.__distro=="nb":
            d="negative binomial"
        elif self.__distro=="p":
            d="poisson"
        elif self.__distro=="u":
            d="uniform"
        else:
            # if i got to this point I have:
            # 1) checked that the distribution is correct
            # 2) that params belong to the distribution
            # 3) that params are numbers
            d="unknown"

        return "{} - {}".format(d,",".join(self.__params))
