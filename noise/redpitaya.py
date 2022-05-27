import time
import numpy as np
import redpitaya_scpi as scpi


class RedPitaya:

    def __init__(self, address, dec_factor, n_samples, duration):
        self.rp_s = scpi.scpi(address)
        self.dec_factor = dec_factor
        self.n_samples = n_samples
        self.duration = duration

    def data_acquisition(self, source, mode):
        self.rp_s.tx_txt('ACQ:RST')  # reset acquisition settings
        time.sleep(1)
        self.rp_s.tx_txt('ACQ:DEC {}'.format(self.dec_factor))  # set the decimation factor
        time.sleep(1)
        self.rp_s.tx_txt('ACQ:{}:GAIN {}'.format(source, mode))  # set the gain mode
        time.sleep(1)
        # self.rp_s.tx_txt('ACQ:TRIG:LEV 0')  # set the triggering level to 0mV
        self.rp_s.tx_txt('ACQ:TRIG:DLY {}'.format(self.n_samples / 2))  # set the trigger to the beginning of the buffer
        time.sleep(1)
        self.rp_s.tx_txt('ACQ:START')  # start acquisition
        time.sleep(1)
        self.rp_s.tx_txt('ACQ:TRIG CH{}_PE'.format(source[-1]))  # trigger the current channel
        time.sleep(1)
        # Wait for trigger. Until trigger is true wait with acquiring
        while 1:
            self.rp_s.tx_txt('ACQ:TRIG:STAT?')
            buff_string = self.rp_s.rx_txt()
            if buff_string == 'TD':
                break

        time.sleep(2 * self.duration)

        self.rp_s.tx_txt('ACQ:' + source + ':DATA?')  # data acquisition

        buff_string = self.rp_s.rx_txt()
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        buffs = np.array(buff_string).astype(float)

        return buffs

    def reset(self):
        self.rp_s.tx_txt('GEN:RST')

    def output(self, source, wave_form, freq, ampl, phase):
        self.rp_s.tx_txt('{}:FUNC {}'.format(source, wave_form.upper()))
        self.rp_s.tx_txt('{}:FREQ:FIX {}'.format(source, freq))
        self.rp_s.tx_txt("{}:PHAS {}".format(source, phase))
        self.rp_s.tx_txt('{}:VOLT {}'.format(source, ampl))

    def output_on(self, source):
        self.rp_s.tx_txt('OUTPUT{}:STATE ON'.format(source[-1]))

    def output_off(self, source):
        self.rp_s.tx_txt('OUTPUT{}:STATE OFF'.format(source[-1]))

    def output_on_all(self):
        self.rp_s.tx_txt("OUTPUT:STATE ON")

    def output_off_all(self):
        self.rp_s.tx_txt("OUTPUT:STATE OFF")

# if __name__ == "__main__":
    # REDPITAYA_ADDRESS = "10.42.0.185"
    # DEC_FACTOR = None
    # N_SAMPLES = None
    # DURATION = None
    # redpitaya = RedPitaya(REDPITAYA_ADDRESS, DEC_FACTOR, N_SAMPLES, DURATION)
    # redpitaya.reset()
    # redpitaya.output(source="SOUR1", wave_form="sine", freq=1000, ampl=0.5, phase=0)
    # redpitaya.output(source="SOUR2", wave_form="sine", freq=1000, ampl=0.5, phase=180)
    # redpitaya.output_on_all()

    # redpitaya.output_off_all()