from colorama import init, Fore, Style
import os
import importlib.util
import sys
from datetime import datetime
import logging

init(autoreset=True)

banner = f"""
{Fore.RED}
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
                                                                                              
{Style.RESET_ALL}"""


class SONiCToolkit:
    def __init__(self):
        self.version = "1.0"
        
    def display_banner(self):
        print(banner)
        
    def list_tools(self):
        return ["IP-tracker", "Bomber", "Email", "Dork_search", "Instagram", 
                "twitter", "Telegram", "WhatsApp", "Discord", "Phone", "Doxing", "FaceAI", "APK"]
    
    def load_tool(self, module_name):
        try:
            module_path = f"tools/{module_name}.py"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"{Fore.RED}Error loading tool: {e}{Style.RESET_ALL}")
            return None
    
    def display_system_status(self):
        print(f"\n{Fore.LIGHTYELLOW_EX}╔══════════════════════════════════════════════════╗")
        print(f"{Fore.LIGHTYELLOW_EX}║{Fore.LIGHTCYAN_EX}               SYSTEM STATUS                  {Fore.LIGHTYELLOW_EX}║")
        print(f"{Fore.LIGHTYELLOW_EX}╠══════════════════════════════════════════════════╣")
        print(f"{Fore.LIGHTYELLOW_EX}║{Fore.LIGHTGREEN_EX} Version: {self.version}{' '*(38-len(self.version))} {Fore.LIGHTYELLOW_EX}║")
        print(f"{Fore.LIGHTYELLOW_EX}║{Fore.LIGHTGREEN_EX} Tools Available: {len(self.list_tools())}{' '*(31-len(str(len(self.list_tools()))))} {Fore.LIGHTYELLOW_EX}║")
        print(f"{Fore.LIGHTYELLOW_EX}║{Fore.LIGHTGREEN_EX} Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}{' '*(24)} {Fore.LIGHTYELLOW_EX}║")
        print(f"{Fore.LIGHTYELLOW_EX}║{Fore.LIGHTGREEN_EX} Author: NoneR00tk1t   {Fore.LIGHTYELLOW_EX}║")
        print(f"{Fore.LIGHTYELLOW_EX}║{Fore.LIGHTGREEN_EX} team: Valhala         {Fore.LIGHTYELLOW_EX}║")
        print(f"{Fore.LIGHTYELLOW_EX}╚══════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    def osint_menu(self):
        while True:
            print(f"""
{Fore.LIGHTRED_EX}╔══════════════════════════════════════════════════╗
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX}               OSINT INVESTIGATION MENU            {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}╠══════════════════════════════════════════════════╣
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 1. Email                                          {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 2. Dork search                                    {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 3. Social Media Analysis                          {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 4. Phone Number                                   {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 5. Doxing                                         {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 6. FaceAI                                         {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 0. Back to Main Menu                              {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}╚══════════════════════════════════════════════════╝
{Style.RESET_ALL}""")
        
            choice = input(f"{Fore.YELLOW}Select OSINT tool (0-6): {Style.RESET_ALL}")
            
            if choice == "1":
                tool = self.load_tool("Email")
                if tool: tool.run()
            elif choice == "2":
                tool = self.load_tool("Dork_search")
                if tool: tool.run()
            elif choice == "3":
                print(f"\n{Fore.LIGHTMAGENTA_EX}Social Media Options:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}1. Instagram")
                print(f"{Fore.CYAN}2. Twitter")
                print(f"{Fore.CYAN}3. Telegram")
                print(f"{Fore.CYAN}4. WhatsApp")
                print(f"{Fore.CYAN}5. Discord")
                sm_choice = input(f"{Fore.YELLOW}Select platform: {Style.RESET_ALL}")
                
                if sm_choice == "1":
                    tool = self.load_tool("Instagram")
                elif sm_choice == "2":
                    tool = self.load_tool("twitter")
                elif sm_choice == "3":
                    tool = self.load_tool("Telegram")
                elif sm_choice == "4":
                    tool = self.load_tool("WhatsApp")
                elif sm_choice == "5":
                    tool = self.load_tool("Discord")
                
                if tool: tool.run()
                
            elif choice == "4":
                tool = self.load_tool("Phone")
                if tool: tool.run()
            elif choice == "5":
                tool = self.load_tool("Doxing")
                if tool: tool.run()
            elif choice == "6":
                tool = self.load_tool("FaceAI")
                if tool: tool.run()
            elif choice == "0":
                return
            else:
                print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")

    
    def phishing_menu(self):
        while True:
            print(f"""
{Fore.LIGHTRED_EX}╔══════════════════════════════════════════════════╗
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX}              PHISHING FRAMEWORK MENU             {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}╠══════════════════════════════════════════════════╣
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 1. Kiya Phisher                                 {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 0. Back to Main Menu                            {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}╚══════════════════════════════════════════════════╝
{Style.RESET_ALL}""")
        
            choice = input(f"{Fore.YELLOW}Select Phishing tool (0-1): {Style.RESET_ALL}")
        
            if choice == "1":
                os.system("bash tools/kiya-phisher.sh")
            elif choice == "0":
                return
            else:
                print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")

    def trojan_menu(self):
        while True:
            print(f"""
{Fore.LIGHTRED_EX}╔══════════════════════════════════════════════════╗
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX}               TROJAN BUILDER MENU               {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}╠══════════════════════════════════════════════════╣
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 1. Android RAT                                  {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 0. Back to Main Menu                            {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}╚══════════════════════════════════════════════════╝
{Style.RESET_ALL}""")
        
            choice = input(f"{Fore.YELLOW}Select Trojan tool (0-1): {Style.RESET_ALL}")
        
            if choice == "1":
                tool = self.load_tool("APK")
                if tool: tool.run()
            elif choice == "0":
                return
            else:
                print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")

    def main_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_banner()
            self.display_system_status()
            
            print(f"""
{Fore.LIGHTRED_EX}╔══════════════════════════════════════════════════╗
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX}                MAIN MENU                     {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}╠══════════════════════════════════════════════════╣
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 1. OSINT Tools                               {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 2. Phishing Tools                            {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 3. Trojan Tools                              {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 4. IP Tracking Tools                         {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 5. Bomber                                    {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 6. List All Available Tools                  {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}║{Fore.LIGHTCYAN_EX} 0. Exit                                      {Fore.LIGHTRED_EX}║
{Fore.LIGHTRED_EX}╚══════════════════════════════════════════════════╝
{Style.RESET_ALL}""")

            choice = input(f"{Fore.YELLOW}Select an option (0-6): {Style.RESET_ALL}")
            
            try:
                if choice == "1":
                    self.osint_menu()
                elif choice == "2":
                    self.phishing_menu()
                elif choice == "3":
                    self.trojan_menu()
                elif choice == "4":
                    tool = self.load_tool("IP-tracker")
                    if tool: tool.run()
                elif choice == "5":
                    tool = self.load_tool("Bomber")
                    if tool: tool.run()
                elif choice == "6":
                    print(f"\n{Fore.LIGHTBLUE_EX}Available Tools:{Style.RESET_ALL}")
                    for tool in self.list_tools():
                        print(f"{Fore.CYAN}- {tool}")
                    input("\nPress Enter to continue...")
                elif choice == "0":
                    print(f"{Fore.RED}Exiting SONiC Toolkit...{Style.RESET_ALL}")
                    sys.exit(0)
                else:
                    print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}Operation cancelled by user.{Style.RESET_ALL}")
                continue
            except Exception as e:
                logging.error(f"Error in main menu: {str(e)}")
                print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
                input("Press Enter to continue...")

if __name__ == "__main__":
    if not os.path.exists("tools"):
        os.makedirs("tools")
        print(f"{Fore.YELLOW}Created 'tools' directory. Please add your tools there.{Style.RESET_ALL}")
    
    toolkit = SONiCToolkit()
    toolkit.main_menu()