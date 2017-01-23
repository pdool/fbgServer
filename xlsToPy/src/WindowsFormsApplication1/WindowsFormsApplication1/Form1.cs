using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml;

namespace WindowsFormsApplication1
{
    public partial class Form1 : Form
    {
        private string xlsLoc = "";
        private string outLoc = "";
        private string pyLoc = "";
        private string pyName = "";
        public Form1()
        {
            InitializeComponent();
            this.Text = "转换工具";
            this.logRt.Width = this.Width;
            readXml();

            this.xlsxLabel.Text = xlsLoc;
            this.outputLabel.Text = outLoc;
            this.pyLabel.Text = pyLoc;

        }

        private void xlsxPath_Click(object sender, EventArgs e)
        {
            OpenFileDialog dlg = new OpenFileDialog();
            dlg.InitialDirectory = this.xlsLoc;
            dlg.Filter = "Excel文件(*.xls;*.xlsx)|*.xls;*.xlsx|所有文件|*.*";


            if (dlg.ShowDialog() == DialogResult.OK)
            {
                xlsLoc = dlg.FileName;
                this.xlsxLabel.Text = xlsLoc;

                string fileName = dlg.SafeFileName;
                this.pyName = fileName.Substring(0,fileName.LastIndexOf(".")) +".py";

                    

            }

        }

        private void outputPath_Click(object sender, EventArgs e)
        {
            FolderBrowserDialog dlg = new FolderBrowserDialog();
            dlg.SelectedPath = this.outLoc;
            if (dlg.ShowDialog() == DialogResult.OK)
            {
                outLoc = dlg.SelectedPath.ToString();
                this.outputLabel.Text = outLoc;
            }

        }

        private void doTrans_Click(object sender, EventArgs e)
        {
            this.logRt.Text = "";
            doExe();
            
        }

        private void scriptBtn_Click(object sender, EventArgs e)
        {
            OpenFileDialog dlg = new OpenFileDialog();
            dlg.InitialDirectory = this.pyLoc;
            dlg.Filter = "py文件(*.py)|*.py";


            if (dlg.ShowDialog() == DialogResult.OK)
            {
                pyLoc = dlg.FileName;
                this.pyLabel.Text = pyLoc;

            }
        }



        public void doExe()
        {

            using (Process process = new System.Diagnostics.Process())
            {
                process.StartInfo.FileName = "python ";
                string cmdStr =  this.pyLoc + " " + this.outLoc + "\\" + this.pyName + " " + this.xlsLoc;
                process.StartInfo.Arguments = cmdStr;
                // 必须禁用操作系统外壳程序  
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.CreateNoWindow = true;
                process.StartInfo.RedirectStandardOutput = true;

                process.Start();

                string output = process.StandardOutput.ReadToEnd();

                if (String.IsNullOrEmpty(output) == false)
                    this.logRt.AppendText(output + "\r\n");

                process.WaitForExit();
                process.Close();
            }
        }


        private void readXml()
        {
            XmlDocument xmlDoc = new XmlDocument();

            xmlDoc.Load( "dataConfig.xml");
            //XmlNode root = xmlDoc.SelectSingleNode("root");
            XmlNode xmlNode1 = xmlDoc.SelectSingleNode("/root/xlslFolder");
            this.xlsLoc = xmlNode1.InnerText;

            XmlNode xmlNode2 = xmlDoc.SelectSingleNode("/root/outputFolder");
            this.outLoc = xmlNode2.InnerText;

            XmlNode xmlNode3 = xmlDoc.SelectSingleNode("/root/scriptPath");
            this.pyLoc = xmlNode3.InnerText;
        }

    }
}
