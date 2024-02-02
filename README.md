# time-varying_syenrgy-extraction

# version

numpyは1.21.6
matplotlibは、3.5.3


# dataの行列の形
data => (自由度, 時間)
synergy => (シナジーの数,自由度,時間)
amplitude =>(シナジーの数, 1)
delays => (シナジーの数, 1 )

amplitudeとdelaysでは、値を取り出して、その値をsynergiesの要素にかけていく。