<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SONiC Toolkit - Advanced OSINT & Penetration Testing Framework</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid #21262d;
        }
        
        .banner {
            font-family: monospace;
            white-space: pre;
            color: #ff6b6b;
            font-size: 8px;
            line-height: 1;
            margin: 20px 0;
            overflow-x: auto;
            text-align: center;
        }
        
        h1 {
            color: #58a6ff;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #f78166;
            border-bottom: 1px solid #21262d;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        
        .description {
            background-color: #161b22;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            border: 1px solid #30363d;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .feature-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            transition: transform 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: #58a6ff;
        }
        
        .feature-card h3 {
            color: #58a6ff;
            margin-top: 0;
        }
        
        .code-block {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            margin: 20px 0;
            font-family: monospace;
        }
        
        .warning {
            background-color: rgba(248, 81, 73, 0.1);
            border-left: 4px solid #f85149;
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }
        
        .btn {
            display: inline-block;
            background-color: #238636;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px 5px;
            transition: background-color 0.3s ease;
        }
        
        .btn:hover {
            background-color: #2ea043;
        }
        
        footer {
            text-align: center;
            padding: 40px 0;
            margin-top: 40px;
            border-top: 1px solid #21262d;
            color: #8b949e;
        }
        
        @media (max-width: 768px) {
            .banner {
                font-size: 5px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .features {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="banner">
                                                  QK                                          
                                                 ORNI                                  Z      
                                                ZTNMNG                                 Z      
              YV YWXZ                          ZUKZVPOE                                    R  
             UXZ                               OMXY HMOG                               Z      
                                              VSK N ZKIMFZ                             Z      
                                            ZGPNZGGL IIJIGZ VGFSUSSSTONKCK                    
                                         LKTLSJPIEEGJ DHIJKKMHKLLLKLKKKKNVLH                  
                                      ZDTQLLIKHJGDGEHEKHHIJLJKJKKJJKKJJJKKLQOF           Y    
                                    YGUOMMLNHKHJEFEFFGEFHJJJIJLKKJJJJJJJJJJKMUE          W    
                                   GNTMNLNJLHIGGGGHGGFFFFGFFEDEFFFFKJJJKKJLMLJVE         TZ   
                                 UISQMKKLKKLLKKLKHGGFFDDDCBBDDCDDDCCBBCEIJKKLJLQK         M   
   WTSTSVU Z                    NJVMMJOMKMLMJFDFFEDDDBCDDDBDDCDDCCDCEFFGIJJKJJJQM           T 
  RRRRTPRRRQTR      U          KKSNNJOMJLIIMLIJKLLGEDEDFGHCFEBACFHIJJJIHJJJKKJJKTY         Z  
QPQOQQQSSTRRRRSW              PHTMNLIJMLLKJIJHGGIMJJHGEDDDEDCFJIJJJIJJIIJJJJJKJJLJ            
PQPPPPQSRRSSSRRT              JPPMMLMMLLLLLKIIGFDFHKJHEDCBBHIHIIJJIIIIIIIJJJJKKGOOMORMNPTSTT  
QQPQQPQSSSSTSRRRW            KGRMLKJILNLLLJGGFFFEFDGKJFEDGHHHIIIJJIIIIIIIIIIJHIKIJGHGHEEDEGFII
USQOQQQSTSTTSQQT             INPKKIMNLMNMKHGEEDDEDEDGJFEEJHHHIIIIIIGHIHKJIIKKJEDEFMX     ZYZFG
USRRSRQQRSTUTSRU             JNJKMJMKKLMMIHGHFFEDFDDEIIDFIHHHHIHHHHIIIIHJIGECCBCDCDDDDCBRZRFFN
URQSRRRQQSTVSSSXYX          WHGKNKLILKLNKJIIHFDEEDDDFGJEHHHHHIHGGGHHJKHBCCCCCCBBBEDCCDDKREHC  
WSQTSRONRSTTUTW             EJIMKJJMKJSPKKIHGGEDDEDDEFJFGIKJIIHIFHKIECCBBCCDEDCBAAECEDEHGFL   
W  STRQSRUWW               HHJMLIJLKKMVOIHHHHGEBDFFEEFIIIHIIIIIIIFDCBBCCDCBBBCCCCCCECDDFG     
XZ         Y             ZKHHKKJJLNJKLTMKKJIHGEFFEFCEFIIHHIIJJJDBCCBBCEEFGFGGGEDDCCEEFFGH     
 W         Z             LHIIJJJLJJOKMTLKLIIGFFJGHMKGFHHHIIJJGEFHHHGHHGFHIGFFFGHIIGHFFHHMW    
 ZY        Y            JKJIKKKILLLPIS ZOLJIHFEJT MJEFJIGIFGHGFFFFCCBBBBCHFGHGIGJHGGFIGJKQ    
 X                     LKKJIMMJLMMMOOVY WUPJHHGIJIKHEGIHJJGGFEEEEBCCCBBBCDGHIKJGHHGFGGGKMQ    
 S                    VKLIHLMLKNMLLMN XL   SJIFFDDFDDCEHECDFHGFEDDBCCCBBCCEIKHIHHHFEHIHKLP    
R                     MKIIJLMLMNNMKPNZ HLR XZMIHGYIEDDECCHHSTJJGCCACBBBCCBGHHHHGJHFGFGKKKP    
                     ULKJJJKMMMMLMKMOZZUJNN   WWPEEEFCECCHHSRHHFCBDCBBCCBGIIIIFIIHEFGFJJFX    
           ST     RR   SKLJKKLONKKLKKSZZQRXUL     NGDFFDCBEEHHFHEHFEECDBGJIHIHHHIGIGGGLKE     
      RLLLL       O      HHIKMPMLJHKJLPZZTYYX J     Z IEDGDDEFDDEDDBIDHJIHGHHIKJDIIJIHJHY     
      KMT        XP      YFJKLNNMKLJKIJLYZVR  ZY L    TRMFFDDDCCDCCDFGGGFGJHKJEECDJJIGLE     V
     WOJ    Z    US     Y YGHLMPLNJJKIJOOOYZWTW Y S MS    W X PQQEGFFFEDFHHJJTCEEEGKJKE       
     VPN   Y Z   SY YZX V W IINKLLHNZIFJJJNISZZPF J  RRNJEICCN YTJEEEEEEGHJIX  RCEEIKHN       
     VNS  Y     XOXPZZZ MVZWWJKILPZYMJLJHIGFHFHTZ ZXKLJLHJW    XHFEEGFGFGIMO     CCGII        
 OL  XOK  U    VVMMOTV V  VXVXHHXZYQJPPKJHGGGGFDDDEIOXZ      SFGJHEDFIHFHLG       CFD         
ONL   LJ  QYY ZVUMJMNNQZ     Z KOYZINMPMKIJGFGGFEDBCBDFDREFEDDDEJHDCGJGIJNV        A          
NMM   MM OMPS Z UNNLNY          KPNNMNZYYYZVMFFDFIDCCFDR TDDCDDGIHDCHIGILK                    
MLJ   MNULKMMLVZ      YZ    YPNMNNIKJVYYYZZZ      WNJKEZ VHGEDCGGHCCIHIIJC                    
MLX Y KLLKNNNW     VQUX   XZ      ZXWOIIIIGGLR     UMIC  ZNFGCEGGHBEGGHIKP                    
NN    RLMLNI     MLNR  WSZ Z ZYTQJKMJHHKHGGGGJIEG    GEI TZFEEEEGHDFFHHJL   NR       Z     U  
MK  Z  YOW     JLNPX WUW     ZXY     ZWMHIHHGHHHGV  ZH JZIZGGHDFGHBHHHJJJ    QLLV USRJLKKLJLX 
NJ  XX       NNNNSZXZ    YYZ        VZ      KKIEN K FJ YO YYEEEFHFCHHHIJF      SJJIJJIIIIIIIJK
QIYXSYWL   RRNONMQ Y             ZLH ZOTPQWZZ    MGJK   G RZIEFFHECHHHIJD       ZIIJIJIJJIIIJI
MZVVNNN  ZZYSVYZYSSSTUTUQLKJLIS   GGLJSZYZ      CJMF    WIWZXBCCHEDJJJJJG      VLJIIJIJJJIIIII
K JMLMO    Z           RNKGP W X  MGKNGJUY   PFHJMKGS    B WZLEBFIHGHIIG        TKIIIIJJIIIIIJ
MW LMPOOJPW         SLMJNVXU ZJ    GKKMHLLKKKIEFKKHEGF   WI WZCFFGFGHIJL        YKKIJJJJJJJIJI
OUX   WLKNLNLOLKMKKKMMQSSSWOKR     NLKKJKJJIIJEGMMKEFGDF  B MZTFEGHGIKE         P  YNJJIIIJIKJ
NZWZ        NMMNMOPQQOOMKIJY       PLLJJKJHFDKGHLLMGGEHJKHDV  ZCDFGHHE          Q   SOOMJILMVO
NYRV         QMKMJLLILHT          VOKJJKKT    NHHLLNN   PCEB  ZVBFEFFY          Q            U
LIMO        S                     GMKJJKK      IGFKNF    QGQTVQPLKLHDL          RZ        Z  P
 HJP        XN      VTTX          LNJJKLP      LIHHKHK     Z    YUOPLCW         UL          YL
           YYPOPSTRRQRQQT         SKJKJKSO     XOKIKHE W   WRPSPNNMLGBT          U          ZO
          YPRQQRQRRRSNPPU        QOIKKKK        LIIIKFU XSXU ZYZXTQQLHEZ                     Q
         SRTRRQQQOORX            KLKJKMG        LKHHJDC      YLHDHOSPKD                      T
     TVPQPQQPQPQRY              XQKLKKLZ         OJILDF  QBDDGKKLIEAJDY                      Z
     RQPQQRNPV     Y            QMLLLLJ          HKKKECQZ     VY    KC                        
    TSRQQRX     Z Z             MHOLKKK          JNKKFGI  Z  Z ZXTNW LE                       
   RRRQR     YW                RNILJKIO           OJLIEO W Y YRSVZZYEZOG                      
 QNRRRQZ   U                   RKLKKJH            LLIJG      PZRPTXZYHZGH                     
 OPRQTY   Z                    NOLKJKE            HMIJ      P  ZRRW  TOZCSZZ                  
ZPQQT                         JMKMILHN            LOL   TW R   ZYVZZ ZRZLF                    
SQPT                          PJJMKHGW            YO  ZZP WR          XU GS                   
PRR                           SJKKJGE             RTTKLFNP V      Z    Z IE                   
RR                           PMJKKIHD             HEGHFHGDN      J   W    D                   
V                            IKKKJHHP              FFEEEDDC   Z TV     WYWET               YVW
                            ZSKLMJIGU              PGHJFCCA   W L   Z    SFP             RQVY 
                            PPIEFHGF               WEFGDDC  ZZH D  XK  YGQDX           RMSP  W
                         ZSMDIEFDDDDBIOZ       CCQ       Z WUKJNW  ZD ROHFG        Z  PNNOSWSP
                     SZ                BDZ    DEZ        MNLHFJBYYQWLVJGFGV      XZ  TZOOOOOPO
                      Z  Y   YVZ       BEY    GEX   P Y WEIDHGCLMGLELD NR          ZZZXSPPPOOO
                          US       U   DE      CDYPLCGGGFFGDFBFHGGGDE           Z  XZ YPPPOONO
                     ZY    SZ QZV  OPBCC       DDHV ZIWZ ORXKFFGHECP         Z  ZZZZ ZRPQPNOOQ
                      YU QXMSYYZO Z    CQ     FDBMPVNNZFONTSGEHGDLZ           Y  X     UPPQRXZ
                   ZVPMIGKIHIIJMNYPHY  EL     FCCCBDGHLCEGJIIIFSVIO               Z   Z      X
                   MDCHJKJLHDDDFIFHIIRBG      ZCCDABCDBBBBABBAACEGN  Z   Z                    
                 LKZYV        ECKJIFCDH        CBCEGCCEZ    ZWUTWTCCH    Q                    
                A  ZGNRJII  W   CGLIHCC        BELHBA    ZVHISONHLG DDM    Z                  
              I   HJJGGGMYOIURY  BDKHDBF      OCGHAAX    UKDGEDDEEDECXCD  ZUYXZY              
             CQOIIIILHIFGGFFIRZ   BEHHBB      BFIADL   WOZEDCCGFEEDFFEEDC    WTWZZZ           
           ORWOKJJJJGJJIIFFGHJKY  NEHHDB     GEIDBB   ZHFEARTGGHDEEFEEFGGBS     O             
          PXSNKJKJHJHKIKIJHEDGHH   BCHGBN    CHFCCX  JEGDBFFW SFFEEFEEEFIGCBT    Z            
       WZLRQLIJJJLLLMPLJKHGGDCGGZ  CBEFCC   OEHEBA   VICCIGEGFX KHIGGGGHIIGCRZZW              
       ZPSUKJKJJIKL RIJJIIHECCDGO  CCCEDA   AFGDBA   ECBIHIIJIIJWLIIIIIIIIJGEYW  SZ        ZYY
      OYNXJIIJILIVSJKKKJJHGDBCD    BCCDEB  NEFEDCA   EBBABGHIIIIJMJIIIIIIIIIDUYY          XTWU
     ZKCXLKJJJLM MIIJJKJIGDBBCDB  BEDEFHDZ ECEFCCB  UBDCBBABBCDEFGGHHIIIIIIIIBXY         WSYZZ
     YDEMHIJJKMWMKLLKKIHEBBCCDDDDDDCCEGGC   ACECCDDKCCCBBBABBBBBBBBBBCCDEEFGJHYW          Z   
       FPWWZ XQDAABCABBDDBDFEDACEHGHGIIHQ     UACCFCEACBAAABBAABQZ    ZRROICEHV               
       SLWZ             ZXSQNLLLJJFJLN             QIHFEMRPOX          XVSNJDDZ               
           ZVXZ     Z ZWRPPNNMJLQZ                                                            
            </div>
            <h1>SONiC Toolkit</h1>
            <p>Advanced OSINT & Penetration Testing Framework for Cybersecurity Professionals</p>
        </header>

        <section class="description">
            <h2>About The Project</h2>
            <p><strong>SONiC Toolkit</strong> is a comprehensive and advanced framework for Open-Source Intelligence (OSINT) gathering and penetration testing, designed for cybersecurity professionals, ethical hackers, and researchers. It provides a centralized suite of tools for digital reconnaissance, vulnerability analysis, and security assessment.</p>
            
            <p>This project is developed in Python and supports various modules for performing advanced security operations. The colorful menu-driven interface makes using the tools easy even for beginner users.</p>
            
            <div class="warning">
                <strong>Warning:</strong> This toolkit is intended for educational purposes and authorized security testing only. Never use these tools on systems or accounts without explicit permission.
            </div>
        </section>

        <section>
            <h2>Features</h2>
            <div class="features">
                <div class="feature-card">
                    <h3>🔍 OSINT Investigation</h3>
                    <p>Gather intelligence from public sources with tools like Email Analysis, Dork Searching, Social Media analysis (Instagram, Twitter, Telegram, WhatsApp, Discord), Phone Number Lookup, Doxing, and FaceAI.</p>
                </div>
                
                <div class="feature-card">
                    <h3>🎣 Phishing Framework</h3>
                    <p>Simulate phishing campaigns for security testing with integrated tools like Kiya Phisher to assess organizational vulnerability to social engineering attacks.</p>
                </div>
                
                <div class="feature-card">
                    <h3>🐍 Trojan Builder</h3>
                    <p>Create payloads for authorized penetration testing with the Android RAT (Remote Access Trojan) Builder for legitimate security assessment purposes.</p>
                </div>
                
                <div class="feature-card">
                    <h3>📡 Reconnaissance</h3>
                    <p>Perform information gathering and footprinting with specialized tools like IP Tracker and Bomber for network analysis and testing.</p>
                </div>
            </div>
        </section>

        <section>
            <h2>Installation</h2>
            <div class="code-block">
git clone https://github.com/NoneR00tk1t/SONiC-Toolkit.git
cd SONiC-Toolkit
pip install -r requirements.txt
python3 sonic.py
            </div>
            
            <p>Requirements: Python 3.x, Colorama</p>
        </section>

        <section>
            <h2>Usage</h2>
            <p>After launching the toolkit, you will be presented with a main menu:</p>
            <ol>
                <li>Select a category (OSINT, Phishing, Trojan, etc.)</li>
                <li>Choose the specific tool you want to use from the sub-menu</li>
                <li>Follow the on-screen instructions provided by each tool</li>
            </ol>
            
            <div class="code-block">
# Example of running the IP-tracker tool
[1] OSINT Tools
[4] IP Tracking Tools
Enter target IP: 192.168.1.1
            </div>
        </section>

        <section>
            <h2>Disclaimer</h2>
            <div class="warning">
                <strong>Important:</strong> This project is for educational and ethical purposes only. The developers are not responsible for any misuse of this toolkit. Always ensure you have proper authorization before testing any system. Unauthorized use may violate laws and regulations.
            </div>
        </section>

        <section>
            <h2>Contributing</h2>
            <p>Contributions are welcome! Please feel free to submit a Pull Request.</p>
            <ol>
                <li>Fork the project</li>
                <li>Create your feature branch (<code>git checkout -b feature/AmazingFeature</code>)</li>
                <li>Commit your changes (<code>git commit -m 'Add some AmazingFeature'</code>)</li>
                <li>Push to the branch (<code>git push origin feature/AmazingFeature</code>)</li>
                <li>Open a Pull Request</li>
            </ol>
        </section>

        <section>
            <h2>License</h2>
            <p>This project is licensed under the MIT License - see the LICENSE file for details.</p>
        </section>

        <footer>
            <p>SONiC Toolkit &copy; 2023 | Developed by NoneR00tk1t | Valhala Team</p>
            <p>
                <a href="#" class="btn">View on GitHub</a>
                <a href="#" class="btn">Report Bug</a>
                <a href="#" class="btn">Request Feature</a>
            </p>
        </footer>
    </div>
</body>
</html>
