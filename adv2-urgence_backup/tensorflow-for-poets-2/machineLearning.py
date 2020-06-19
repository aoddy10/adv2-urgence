
import subprocess


class MachineLearning:

    # get prediction from ML
    def getPrediction(self, sourceFileLocation):
        # ML model location
        modelPb = "tensorflow-for-poets-2/tf_files/retrained_graph.pb"
        modelLabels = "tensorflow-for-poets-2/tf_files/retrained_labels.txt"

        # create command
        cmd = "python3 -m tensorflow-for-poets-2.scripts.label_image --image=" + \
            sourceFileLocation + " --graph=" + modelPb + " --labels=" + modelLabels

        print(cmd)
        # cmd = ["chmod u+x tensorflow-for-poets-2/scripts/label_image.py",
        # "tensorflow-for-poets-2/scripts/label_image.py --image=tensorflow-for-poets-2/tf_files/data_set/collapsed/download.jpeg --graph=tensorflow-for-poets-2/tf_files/retrained_graph.pb --labels=tensorflow-for-poets-2/tf_files/retrained_labels.txt"]

        # run command
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        (output, err) = p.communicate()

        p_status = p.wait()

        # print "Command output : ", output
        print output
        return output
