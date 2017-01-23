namespace WindowsFormsApplication1
{
    partial class Form1
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.doTrans = new System.Windows.Forms.Button();
            this.xlsxPath = new System.Windows.Forms.Button();
            this.outputPath = new System.Windows.Forms.Button();
            this.xlsxLabel = new System.Windows.Forms.Label();
            this.outputLabel = new System.Windows.Forms.Label();
            this.scriptBtn = new System.Windows.Forms.Button();
            this.pyLabel = new System.Windows.Forms.Label();
            this.logRt = new System.Windows.Forms.RichTextBox();
            this.SuspendLayout();
            // 
            // doTrans
            // 
            this.doTrans.Location = new System.Drawing.Point(2, 213);
            this.doTrans.Name = "doTrans";
            this.doTrans.Size = new System.Drawing.Size(75, 23);
            this.doTrans.TabIndex = 0;
            this.doTrans.Text = "转换";
            this.doTrans.UseVisualStyleBackColor = true;
            this.doTrans.Click += new System.EventHandler(this.doTrans_Click);
            // 
            // xlsxPath
            // 
            this.xlsxPath.Location = new System.Drawing.Point(2, 49);
            this.xlsxPath.Name = "xlsxPath";
            this.xlsxPath.Size = new System.Drawing.Size(75, 23);
            this.xlsxPath.TabIndex = 1;
            this.xlsxPath.Text = "xlsx路径：";
            this.xlsxPath.UseVisualStyleBackColor = true;
            this.xlsxPath.Click += new System.EventHandler(this.xlsxPath_Click);
            // 
            // outputPath
            // 
            this.outputPath.Location = new System.Drawing.Point(2, 115);
            this.outputPath.Name = "outputPath";
            this.outputPath.Size = new System.Drawing.Size(75, 23);
            this.outputPath.TabIndex = 2;
            this.outputPath.Text = "输出地址：";
            this.outputPath.UseVisualStyleBackColor = true;
            this.outputPath.Click += new System.EventHandler(this.outputPath_Click);
            // 
            // xlsxLabel
            // 
            this.xlsxLabel.AutoSize = true;
            this.xlsxLabel.Location = new System.Drawing.Point(83, 54);
            this.xlsxLabel.Name = "xlsxLabel";
            this.xlsxLabel.Size = new System.Drawing.Size(293, 12);
            this.xlsxLabel.TabIndex = 3;
            this.xlsxLabel.Text = "E:\\FBG\\Server\\kbengine\\kbe\\tools\\xlsx2py\\rpgdemo";
            // 
            // outputLabel
            // 
            this.outputLabel.AutoSize = true;
            this.outputLabel.Location = new System.Drawing.Point(83, 120);
            this.outputLabel.Name = "outputLabel";
            this.outputLabel.Size = new System.Drawing.Size(293, 12);
            this.outputLabel.TabIndex = 4;
            this.outputLabel.Text = "E:\\FBG\\Server\\kbengine\\kbe\\tools\\xlsx2py\\rpgdemo";
            // 
            // scriptBtn
            // 
            this.scriptBtn.Location = new System.Drawing.Point(2, 161);
            this.scriptBtn.Name = "scriptBtn";
            this.scriptBtn.Size = new System.Drawing.Size(75, 23);
            this.scriptBtn.TabIndex = 5;
            this.scriptBtn.Text = "脚本所在地址";
            this.scriptBtn.UseVisualStyleBackColor = true;
            this.scriptBtn.Click += new System.EventHandler(this.scriptBtn_Click);
            // 
            // pyLabel
            // 
            this.pyLabel.AutoSize = true;
            this.pyLabel.Location = new System.Drawing.Point(83, 166);
            this.pyLabel.Name = "pyLabel";
            this.pyLabel.Size = new System.Drawing.Size(359, 12);
            this.pyLabel.TabIndex = 6;
            this.pyLabel.Text = "E:\\FBG\\Server\\kbengine\\kbe\\tools\\xlsx2py\\xlsx2py\\xlsx2py.py";
            // 
            // logRt
            // 
            this.logRt.Location = new System.Drawing.Point(2, 254);
            this.logRt.Name = "logRt";
            this.logRt.Size = new System.Drawing.Size(670, 280);
            this.logRt.TabIndex = 8;
            this.logRt.Text = "";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(673, 533);
            this.Controls.Add(this.logRt);
            this.Controls.Add(this.pyLabel);
            this.Controls.Add(this.scriptBtn);
            this.Controls.Add(this.outputLabel);
            this.Controls.Add(this.xlsxLabel);
            this.Controls.Add(this.outputPath);
            this.Controls.Add(this.xlsxPath);
            this.Controls.Add(this.doTrans);
            this.Name = "Form1";
            this.Text = "Form1";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button doTrans;
        private System.Windows.Forms.Button xlsxPath;
        private System.Windows.Forms.Button outputPath;
        private System.Windows.Forms.Label xlsxLabel;
        private System.Windows.Forms.Label outputLabel;
        private System.Windows.Forms.Button scriptBtn;
        private System.Windows.Forms.Label pyLabel;
        private System.Windows.Forms.RichTextBox logRt;
    }
}

